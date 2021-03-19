import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import { AfterViewInit, Component, OnDestroy, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
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
  loadCount = 0;
  loadMax = 1;
  timeouts = [];
  subscription: Subscription;

  constructor(
    private accountService: AccountService,
    private alertService: AlertService,
    private tickerService: TickerService,
    public dialog: MatDialog
  ) {
    this.subscription = this.accountService.logoutAnnounced$.subscribe(() =>
      this.clearAllTimers()
    );
  }

  ngAfterViewInit(): void {
    this.loadCount = 0;
    this.tickerService
      .getAllTickers()
      .toPromise()
      .then(
        (tickers) => {
          this.loadMax = tickers.length;
          tickers.forEach((symbol) => {
            this.tickerService
              .getTickerPrediction(symbol)
              .toPromise()
              .then(
                (result) => {
                  this.tickers.push(result);
                  this.startTimer(result);
                  this.loadCount++;
                },
                (err) => {
                  this.alertService.error(err.error.message);
                  this.loadCount++;
                }
              );
          });
        },
        (err) => {
          this.alertService.error(err.error.message);
          this.loadCount = this.loadMax;
        }
      );
  }

  ngOnInit(): void {}

  ngOnDestroy() {
    // prevent memory leak when component destroyed
    this.subscription.unsubscribe();
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
            this.tickers.push(result);
            this.isAdding = false;
          },
          (err) => {
            this.alertService.error(err.error.message);
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
              (result) => {
                this.tickers.splice(index, 1);
              },
              (error) => this.alertService.error(error.error.message)
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

  startTimer(ticker: Ticker) {
    this.timeouts.push(
      setTimeout(() => {
        if (this.tickers.indexOf(ticker) < 0) return;
        this.tickerService
          .getTickerPrediction(ticker.ticker)
          .toPromise()
          .then((result) => {
            if (this.tickers.indexOf(ticker) < 0) return;
            this.tickers[this.tickers.indexOf(ticker)] = result;
            this.startTimer(result);
          });
      }, ticker.multiplier * 60000)
    );
  }

  clearAllTimers() {
    this.timeouts.forEach((to) => clearTimeout(to));
  }
}
