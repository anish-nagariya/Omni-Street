import { Component } from '@angular/core';
import { Account } from './_models';
import { AccountService } from './_services';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  account: Account;

  constructor(private accountService: AccountService) {
    accountService.account.subscribe((x) => (this.account = x));
  }

  title = 'frontend';

  logout() {
    this.accountService.logout();
  }
}
