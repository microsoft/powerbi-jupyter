// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.

import { models, Page, Report } from 'powerbi-client';
import { ReportView } from './report';

/**
 * Returns width and height of the active page as an object
 * @param report PowerBI Report
 */
export async function getActivePageSize(report: Report): Promise<models.ICustomPageSize> {
  const pages = await report.getPages();

  // Get the active page
  const activePage = pages.find((page) => {
    return page.isActive;
  });

  if (!activePage) {
    throw 'No active report page';
  }

  return activePage.defaultSize;
}

export async function getRequestedPage(report: Report, pageName: string): Promise<Page> {
  const pages: Page[] = await report.getPages();
  const requestedPage: Page = pages.filter((page: Page) => {
    return page.name === pageName;
  })[0];

  if (!requestedPage) {
    throw 'Page not found';
  }

  return requestedPage;
}

/**
 * Returns width and height of the active page as an object
 * @param tokenExpiration Access token expiration timestamp
 * @param minutesToRefresh Minutes before expiration
 * @param reportView ReportView
 */
export async function setTokenExpirationListener(
  tokenExpiration: number,
  minutesToRefresh: number,
  reportView: ReportView
): Promise<void> {
  // Get current time
  const currentTime = Date.now();
  const expiration = tokenExpiration * 1000;
  const safetyInterval = minutesToRefresh * 60 * 1000;

  // Time until token refresh in milliseconds
  const timeout = expiration - currentTime - safetyInterval;

  // If timeout reaches safetyInterval, invoke the setTokenExpiredFlag method
  if (timeout <= 0) {
    reportView.setTokenExpiredFlag();
  } else {
    // Set timeout so minutesToRefresh minutes before token expires, setTokenExpiredFlag will be invoked
    console.log('Report Access Token will be updated in ' + timeout + ' milliseconds.');
    setTimeout(() => {
      reportView.setTokenExpiredFlag();
    }, timeout);
  }
}
