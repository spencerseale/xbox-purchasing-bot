
import selenium
from selenium import webdriver
from typing import Optional
import time
import logging
import argparse
from importlib_resources import files
import toml

def _purchase_item(
    web_driver: webdriver.safari.webdriver.WebDriver,
    item: str,
    load_time: int
) -> None:
    """ Iteratively refresh amazon page until "Buy now" button appears
        Purhcase item once button goes live and break refreshing.
    """

    purchased = False

    while True:

        try:

            web_driver.find_element_by_id("buy-now-button").click()

            time.sleep(load_time + 3)

            web_driver.find_element_by_name("placeYourOrder1").click()

            time.sleep(load_time + 60)

            logging.info("Purchase complete!")

            break

        except selenium.common.exceptions.NoSuchElementException:

            logging.info("%s not currently available... trying again." % item)

            time.sleep(8)

            web_driver.refresh()

            time.sleep(2)

            continue

def main(
    url_suffix: Optional[str] = None,  # defaults to Xbox Series X
    amzn_creds: str = "amazon_creds.toml",
    low_speed_internet: bool = False
) -> None:
    """ High-level runner for AMZN bot.

    Args:
        url_suffix: all parts of AMZN url str (i.e. amazon.com/<url_suffix>)
    """

    if not url_suffix:

        logging.info(
            "Since you didn't specify an Amazon URL suffix, we will assume "
                "you're a sucker and STILL can't get an Xbox Series X!"
        )

        url_suffix = (
            "Xbox-X/dp/B08H75RTZ8/ref=sr_1_10?dchild=1&keywords="
                "xbox+series+x&qid=1632367889&sr=8-10"
        )

        item = "xbox_series_x"

    else:

        item = "over_hyped_useless_item"

    logging.info(
        "Hang tight while we connect to Safari and buy you a %s" % item
    )

    load_time = 6 if low_speed_internet else 2

    # open safari and navigate to amazon product page
    driver = webdriver.Safari()

    driver.get(f"https://www.amazon.com/{url_suffix}")
    time.sleep(load_time - 1)  # generally readily available

    ### login

    # get amazon creds
    amzn_auth = toml.loads(files("configs").joinpath(amzn_creds).read_text())

    sign_on = driver.find_element_by_id("nav-link-accountList-nav-line-1").click()
    time.sleep(load_time)

    # email input
    email_txt_box = driver.find_element_by_id("ap_email")
    time.sleep(load_time)
    email_txt_box.send_keys(amzn_auth["user"])
    driver.find_element_by_id("continue").click()
    time.sleep(load_time)

    # password input
    pass_txt_box = driver.find_element_by_id("ap_password")
    time.sleep(load_time)
    pass_txt_box.send_keys(amzn_auth["password"])
    driver.find_element_by_id("signInSubmit").click()
    time.sleep(load_time)

    # perform iterative refreshing and attempt to purchase
    _purchase_item(
        web_driver = driver,
        item = item,
        load_time = load_time
    )

if __name__ == "__main__":

    logging.basicConfig(
        level = logging.INFO,
        format = "%(asctime)s -- %(message)s\n",
        datefmt = "%d-%b-%y %H:%M:%S"
    )

    parser = argparse.ArgumentParser(
        description = "Employ bots for personal purchasing of an Xbox Series X."
    )

    parser.add_argument(
        "-u",
        "--url",
        default = None,
        help = "url str following .com/ to locate Amazon product"
    )

    parser.add_argument(
        "-s",
        "--slow_internet",
        action = "store_true",
        default = False,
        help = "Increase wait time between webdriver actions for slower internet."
    )

    args = parser.parse_args()

    # BUY, BUY, BUY!
    main(
        url_suffix = args.url,
        low_speed_internet = args.slow_internet
    )
