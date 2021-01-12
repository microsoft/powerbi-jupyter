import { models, Report } from 'powerbi-client';

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
