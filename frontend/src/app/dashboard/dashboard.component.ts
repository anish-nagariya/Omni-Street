import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import { AfterViewInit, Component, OnDestroy, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { CountdownConfig, CountdownEvent } from 'ngx-countdown';
import { Subscription } from 'rxjs';
import { ConfirmDialogComponent } from '../_components';
import { Dialog, Ticker } from '../_models';
import { AccountService, AlertService, TickerService } from '../_services';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit, AfterViewInit, OnDestroy {
  tickers: Ticker[] = [];
  newTicker: string;
  index = 0;
  isAdding = false;
  subscription: Subscription;
  countdownConfig: CountdownConfig;
  tickerTaskMap = new Map<string, string>();
  interval;
  deletedTicker: string[] = [];
  maxTickerCount: number;

  constructor(
    private accountService: AccountService,
    private alertService: AlertService,
    private tickerService: TickerService,
    public dialog: MatDialog
  ) {
    this.startCountdown();
    this.subscription = this.accountService.logoutAnnounced$.subscribe(() =>
      this.clearInterval()
    );
  }

  ngAfterViewInit(): void {
    this.tickerService
      .getAllTickers()
      .toPromise()
      .then(
        (tickers) => {
          this.maxTickerCount = tickers.length;
          tickers.forEach((symbol) => this.startTickerPrediction(symbol));
        },
        (err) => {
          this.alertService.error(err);
        }
      );
  }

  ngOnInit(): void {
    this.startInterval();
  }

  ngOnDestroy() {
    // prevent memory leak when component destroyed
    this.subscription.unsubscribe();
    this.clearInterval();
  }
  addTicker() {
    if (
      this.newTicker &&
      this.tickers.some((x) => x.ticker === this.newTicker)
    ) {
      this.alertService.warn(`${this.newTicker} has already been added`);
      return;
    }

    if (this.tickers.length < 20) {
      this.isAdding = true;
      this.tickerService
        .addTicker(this.newTicker)
        .toPromise()
        .then(
          (result) => {
            console.log(result);

            const index = this.deletedTicker.indexOf(result.ticker);
            if (index >= 0) this.deletedTicker.splice(index, 1);

            this.tickers.push(result);
            this.maxTickerCount = this.tickers.length;
            this.isAdding = false;
          },
          (err) => {
            this.alertService.error(err);
            this.isAdding = false;
          }
        );
    } else
      this.alertService.warn('No more than 20 tickers be added to your list');

    this.newTicker = '';
  }

  deleteTicker(ticker: Ticker) {
    const index = this.tickers.indexOf(ticker);
    if (index > -1) {
      let data: Dialog = {
        message: `Do you want to delete "${ticker.ticker}"?`,
        title: 'Confirm Delete',
      };
      const dialogRef = this.dialog.open(ConfirmDialogComponent, {
        data: data,
      });

      dialogRef.afterClosed().subscribe((result) => {
        if (result) {
          this.tickerService
            .deleteTicker(ticker.ticker)
            .toPromise()
            .then(
              () => {
                this.deletedTicker.push(ticker.ticker);
                this.tickers.splice(index, 1);
                this.maxTickerCount = this.tickers.length;
              },
              (err) => this.alertService.error(err)
            );
        }
      });
    }
  }

  drop(event: CdkDragDrop<any>) {
    moveItemInArray(
      this.tickers,
      event.previousContainer.data.index,
      event.container.data.index
    );
  }

  convertToString(num: number) {
    if (num / 1000000000 > 1) return (num / 1000000000).toFixed(3) + 'B';
    else if (num / 1000000 > 1) return (num / 1000000).toFixed(3) + 'M';
    else if (num / 1000 > 1) return (num / 1000).toFixed(3) + 'K';
    else return num.toFixed(2);
  }

  countdownComplete(event: CountdownEvent) {
    if (event.action !== 'done') return;
    this.startCountdown();

    if (this.tickers.length == 0) return;
    this.tickers.forEach((ticker) => this.startTickerPrediction(ticker.ticker));
  }

  private startTickerPrediction(ticker: string) {
    this.tickerService
      .startTickerPrediction(ticker)
      .subscribe((result) =>
        this.tickerTaskMap.set(result.ticker, result.taskId)
      );
  }

  startCountdown() {
    let coeff = 1000 * 60 * 5;
    let nextDateTime: Date = new Date(
      Math.ceil(new Date().getTime() / coeff) * coeff + 60 * 1000
    );
    this.countdownConfig = {
      format: 'm:ss',
      stopTime: nextDateTime.getTime(),
    };
  }

  startInterval() {
    this.interval = setInterval(() => {
      if (!this.tickerTaskMap.size) return;
      this.tickerTaskMap.forEach((taskId, ticker) => {
        if (this.deletedTicker.includes(ticker)) {
          this.tickerTaskMap.delete(ticker);
          return;
        }
        this.tickerService
          .checkTickerPredictionStatus(taskId)
          .subscribe((result) => {
            if (typeof result !== 'string') {
              const index = this.tickers
                .map((item) => item.ticker)
                .indexOf(result.ticker);
              if (index >= 0) this.tickers[index] = result;
              else if (!this.deletedTicker.includes(result.ticker))
                this.tickers.push(result);
              this.tickerTaskMap.delete(result.ticker);
            } else {
              console.log(result);
              if (this.tickerTaskMap.has(result)) {
                this.tickerTaskMap.delete(result);
                this.maxTickerCount--;
                this.tickerService.deleteTicker(result).subscribe();
              }
            }
          });
      });
    }, 5000);
  }

  clearInterval() {
    clearInterval(this.interval);
  }
}
