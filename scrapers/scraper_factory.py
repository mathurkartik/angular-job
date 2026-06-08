from scrapers.base_scraper import BaseScraper
from scrapers.generic_scraper import GenericScraper
from scrapers.workday_scraper import WorkdayScraper
from scrapers.greenhouse_scraper import GreenhouseScraper
from scrapers.lever_scraper import LeverScraper
from scrapers.remote_board_scraper import RemoteBoardScraper
from scrapers.talent_network_scraper import TalentNetworkScraper

def get_scraper(portal_type: str, headless: bool = True) -> BaseScraper:
    """
    Factory method to instantiate the correct scraper based on portal type.
    """
    if portal_type == "workday":
        return WorkdayScraper(headless=headless)
    elif portal_type == "greenhouse":
        return GreenhouseScraper(headless=headless)
    elif portal_type == "lever":
        return LeverScraper(headless=headless)
    elif portal_type == "remote_board":
        return RemoteBoardScraper(headless=headless)
    elif portal_type == "talent_network":
        return TalentNetworkScraper(headless=headless)
    else:
        return GenericScraper(headless=headless)
