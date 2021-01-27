import { models, Page, Report } from 'powerbi-client';

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
