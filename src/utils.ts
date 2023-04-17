// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.

import { models, Page, Report, service, factories } from 'powerbi-client';
import { QuickVisualizeView } from './quickVisualize';
import { ReportView } from './report';
import { MODULE_VERSION } from './version';

// Jupyter SDK type to be passed with service instance creation
const JUPYTER_SDK_TYPE = 'powerbi-jupyter';

// Initialize powerbi service
export const powerbi = new service.Service(
  factories.hpmFactory,
  factories.wpmpFactory,
  factories.routerFactory,
  { type: JUPYTER_SDK_TYPE, sdkWrapperVersion: MODULE_VERSION }
);

// Set threshold to refresh token in minutes
const TOKEN_REFRESH_THRESHOLD = 10;

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
 * Set token expiration listener
 * @param accessToken 
 * @param widgetView ReportView | QuickVisualizeView
 */
export function setTokenExpirationListener(accessToken: string, widgetView: ReportView | QuickVisualizeView): void {
  const timeout = getTokenExpirationTimeout(accessToken);

  // If timeout reaches safetyInterval, invoke the setTokenExpiredFlag method
  if (timeout <= 0) {
    widgetView.setTokenExpiredFlag();
  } else {
    // Set timeout so minutesToRefresh minutes before token expires, setTokenExpiredFlag will be invoked
    console.log('Access Token will expire in ' + timeout + ' milliseconds.');
    setTimeout(() => {
      widgetView.setTokenExpiredFlag();
    }, timeout);
  }
}

/**
 * Parse the given token and get the expiration timeout
 * @param token 
 */
export function getTokenExpirationTimeout(token: string): number {
  const tokenExpiration = tryGetTokenExpiration(token);

  if (!tokenExpiration) {
    return 0;
  }

  // Get current time
  const currentTime = Date.now();
  const expiration = tokenExpiration * 1000;
  const safetyInterval = TOKEN_REFRESH_THRESHOLD * 60 * 1000;

  // Time until token refresh in milliseconds
  return expiration - currentTime - safetyInterval;
}

// window.atob() won't decode the access token with unicodes properly. So, we are using from bytestream, to percent-encoding, to original string.
// reference: https://developer.mozilla.org/en-US/docs/Web/API/WindowBase64/Base64_encoding_and_decoding#The_Unicode_Problem
// reference: https://stackoverflow.com/questions/38552003/how-to-decode-jwt-token-in-javascript-without-using-a-library/38552302#38552302
function parseJSONWebToken(token: string): any {
  let payload: string;
  const encodedPayload = token.split('.')[1];
  // Fix for parsing the access token with unicode characters Bug: 261401
  payload = encodedPayload.replace(/-/g, '+').replace(/_/g, '/');

  var jsonPayload = decodeURIComponent(atob(payload).split('').map(function (c) {
    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
  }).join(''));

  return JSON.parse(jsonPayload);
}

/**
 * Parse the given token and get the expiration timestamp
 * @param token 
 */
function tryGetTokenExpiration(token: string): number | undefined {
  if (!token) {
    return undefined;
  }

  try {
    const tokenDetails = parseJSONWebToken(token);
    return tokenDetails?.exp;
  } catch (ex) {
    return undefined;
  }
}
