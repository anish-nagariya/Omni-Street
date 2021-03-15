import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { toUnicode } from 'punycode';
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
    return this.http.get<Ticker>(
      baseUrl + `/${symbol}/${multiplier}/${horizon}`,
      { withCredentials: true }
    );
  }
}
