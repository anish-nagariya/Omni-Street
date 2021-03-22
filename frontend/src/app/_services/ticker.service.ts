import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { Ticker } from '../_models';
import { AccountService } from './account.service';

const baseUrl = `${environment.apiUrl}/tickers`;

@Injectable({
  providedIn: 'root',
})
export class TickerService {
  constructor(
    private http: HttpClient,
    private accountService: AccountService
  ) {}

  getAllTickers() {
    return this.http.get<string[]>(baseUrl, { withCredentials: true });
  }

  addTicker(symbol: string): Observable<Ticker> {
    return this.http.put<Ticker>(
      baseUrl,
      { symbol: symbol },
      { withCredentials: true }
    );
  }

  deleteTicker(symbol: string) {
    return this.http.request('delete', baseUrl, {
      body: { symbol: symbol },
      withCredentials: true,
    });
  }

  getTickerPrediction(
    symbol: string,
    multiplier: number = 5,
    horizon: string = 'minute'
  ): Observable<Ticker> {
    return this.http.request<Ticker>(
      'get',
      baseUrl + `/${symbol}/${multiplier}/${horizon}`,
      {
        body: { key: environment.apiKey },
        withCredentials: true,
      }
    );
  }

  startTickerPrediction(
    symbol: string,
    multiplier: number = 5,
    horizon: string = 'minute'
  ): Observable<any> {
    return this.http.post<any>(
      baseUrl + '/task',
      { ticker: symbol, multiplier: multiplier, horizon: horizon },
      { withCredentials: true }
    );
  }

  checkTickerPredictionStatus(taskId: string): Observable<Ticker | string> {
    return this.http.get<Ticker | string>(baseUrl + `/task/${taskId}`, {
      withCredentials: true,
    });
  }
}
