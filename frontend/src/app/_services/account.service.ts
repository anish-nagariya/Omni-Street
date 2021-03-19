import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { finalize, map } from 'rxjs/operators';

import { environment } from 'src/environments/environment';
import { Account } from '../_models';

const baseUrl = `${environment.apiUrl}/accounts`;
const accountsKey = 'omni-accounts-local';

@Injectable({
  providedIn: 'root',
})
export class AccountService {
  private accountSubject: BehaviorSubject<Account>;
  private logoutAnnouncedSource = new Subject<string>();

  public account: Observable<Account>;
  public logoutAnnounced$ = this.logoutAnnouncedSource.asObservable();

  constructor(private router: Router, private http: HttpClient) {
    this.accountSubject = new BehaviorSubject<Account>(
      JSON.parse(localStorage.getItem(accountsKey))
    );
    this.account = this.accountSubject.asObservable();
  }

  public get accountValue(): Account {
    return this.accountSubject.value;
  }

  login(username: string, password: string) {
    return this.http
      .post<any>(
        `${baseUrl}/authenticate`,
        { username, password },
        { withCredentials: true }
      )
      .pipe(
        map((account) => {
          localStorage.setItem(accountsKey, JSON.stringify(account));
          this.accountSubject.next(account);
          this.startRefreshTokenTimer();
          return account;
        })
      );
  }

  logout() {
    this.logoutAnnouncedSource.next();
    this.http
      .post<any>(`${baseUrl}/revoke-token`, {}, { withCredentials: true })
      .subscribe();
    localStorage.removeItem(accountsKey);
    this.stopRefreshTokenTimer();
    this.accountSubject.next(null);
    this.router.navigate(['/account/login']);
  }

  refreshToken() {
    return this.http
      .post<any>(`${baseUrl}/refresh-token`, {}, { withCredentials: true })
      .pipe(
        map((account) => {
          this.accountSubject.next(account);
          this.startRefreshTokenTimer();
          return account;
        })
      );
  }

  register(account: Account) {
    delete account['confirmPassword'];
    return this.http.post(`${baseUrl}/register`, account);
  }

  verifyEmail(token: string) {
    return this.http.post(`${baseUrl}/verify-email`, { token });
  }

  forgot(email: string) {
    return this.http.post(`${baseUrl}/forgot`, { email });
  }

  validateResetToken(resetToken: string) {
    return this.http.post(`${baseUrl}/validate-reset-token`, { resetToken });
  }

  resetPassword(resetToken: string, password: string, confirmPassword: string) {
    return this.http.post(`${baseUrl}/reset-password`, {
      resetToken,
      password,
      confirmPassword,
    });
  }

  getAll() {
    return this.http.get<Account[]>(baseUrl);
  }

  getById(id: string) {
    return this.http.get<Account>(`${baseUrl}/${id}`);
  }

  create(params) {
    return this.http.post(baseUrl, params);
  }

  update(id, params) {
    return this.http.put(`${baseUrl}/${id}`, params).pipe(
      map((account: any) => {
        // update the current account if it was updated
        if (account.id === this.accountValue.id) {
          // publish updated account to subscribers
          account = { ...this.accountValue, ...account };
          this.accountSubject.next(account);
        }
        return account;
      })
    );
  }

  delete(id: string) {
    return this.http.delete(`${baseUrl}/${id}`).pipe(
      finalize(() => {
        // auto logout if the logged in account was deleted
        if (id === this.accountValue.id) this.logout();
      })
    );
  }

  // helper methods

  private refreshTokenTimeout;

  private startRefreshTokenTimer() {
    // parse json object from base64 encoded jwt token
    const jwtToken = JSON.parse(atob(this.accountValue.jwtToken.split('.')[1]));

    // set a timeout to refresh the token a minute before it expires
    const expires = new Date(jwtToken.exp * 1000);
    const timeout = expires.getTime() - Date.now() - 60 * 1000;
    this.refreshTokenTimeout = setTimeout(
      () => this.refreshToken().subscribe(),
      timeout
    );
  }

  private stopRefreshTokenTimer() {
    clearTimeout(this.refreshTokenTimeout);
  }
}
