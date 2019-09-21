# # BOM Manager FindChips Plugin
#
# A BOM Manager plugin for obtaining Pricing AND Availability (PANDA) from FindChips.Com.
#
# ## License
#
# MIT License
#
# Copyright (c) 2019 Wayne C. Gramlich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Packages need by this module:
from bom_manager import bom
from bom_manager.tracing import trace
import bs4
from currency_converter import CurrencyConverter
import re
import requests
import time

# FindChips:
class FindChips(bom.Panda):

    # FindChips.__init__():
    @trace(1)
    def __init__(self, tracing=""):
        # Verify argument types:
        assert isinstance(tracing, str)

        # Initialize the super class of the *FindChips* object (i.e. *self*):
        super().__init__("FindChips")

    # FindChips.__str__():
    def __str__(self):
        panda = self
        return f"Panda('FindChips')"

    # FindChips.vendor_parts_lookup():
    @trace(1)
    def vendor_parts_lookup(self, actual_part, search_name, tracing=""):
        # Verify argument types:
        assert isinstance(actual_part, bom.ActualPart)
        assert isinstance(search_name, str)
        assert isinstance(tracing, str)

        # Grab some values from *actual_part* (i.e. *self*):
        manufacturer_part_name = actual_part.manufacturer_part_name
        original_manufacturer_part_name = manufacturer_part_name

        assert False, "Find chips is FINALLY beding called again!"

        # Trace every time we send a message to findchips:
        if tracing:
            print(f"{tracing}manufacturer_part_name='{manufacturer_part_name}'")

        # Grab a page of information about *part_name* using *findchips_url*:
        url_part_name = bom.Encode.to_url(manufacturer_part_name)
        findchips_url = "http://www.findchips.com/search/" + url_part_name
        if tracing:
            print(f"{tracing}findchips_url='findchips_url'")
        findchips_response = requests.get(findchips_url)
        findchips_text = findchips_response.text.encode("ascii", "ignore")

        # Parse the *findchips_text* into *find_chips_tree*:
        findchips_tree = bs4.BeautifulSoup(findchips_text, "html.parser")

        # if trace:
        #    print(findchips_tree.prettify())

        # We use regular expressions to strip out unnecessary characters
        # in numbrers:
        digits_only_re = re.compile("\\D")

        # Result is returned in *vendor_parts*:
        vendor_parts = list()

        # Currently, there is a <div class="distributor_results"> tag for
        # each distributor:
        for distributor_tree in findchips_tree.find_all("div", class_="distributor-results"):
            # if trace:
            #        print("**************************************************")
            #        print(distributor_tree.prettify())

            # The vendor name is burried in:
            #   <h3 class="distributor-title"><a ...>vendor name</a></h3>:
            vendor_name = None
            for h3_tree in distributor_tree.find_all(
              "h3", class_="distributor-title"):
                # print("&&&&&&&&&&&&&&&&&&&&&&&")
                # print(h3_tree.prettify())
                for a_tree in h3_tree.find_all("a"):
                    vendor_name = a_tree.get_text().strip()

            # If we can not extact a valid *vendor_name* there is no
            # point in continuing to work on this *distributor_tree*:
            if vendor_name is None:
                continue

            # This code is in the *VendorPart* initialize now:
            # Strip some boring stuff off the end of *vendor_name*:
            # vendor_name = text_filter(vendor_name, str.isprintable)
            if vendor_name.endswith("Authorized Distributor"):
                # Remove "Authorized Distributor" from end
                # of *vendor_name*:
                if vendor_name.endswith("Authorized Distributor"):
                    vendor_name = vendor_name[:-22].strip(" ")
                if vendor_name.endswith("Member"):
                    # Remove "Member" from end of *vendor_name*:
                    vendor_name = vendor_name[:-6].strip(" ")
                if vendor_name.endswith("ECIA (NEDA)"):
                    # Remove "ECIA (NEDA)" from end of *vendor_name*:
                    vendor_name = vendor_name[:-11].strip(" ")

            # Extract *currency* from *distributor_tree*:
            currency = "USD"
            try:
                currency = distributor_tree["data-currencycode"]
            except ValueError:
                pass

            # All of the remaining information is found in <table>...</table>:
            for table_tree in distributor_tree.find_all("table"):
                # print(table_tree.prettify())

                # There two rows per table.  The first row has the headings
                # and the second row has the data.  The one with the data
                # has a class of "row" -- <row clase="row"...> ... </row>:
                for row_tree in table_tree.find_all("tr", class_="row"):
                    # Now we grab the *vendor_part_name*.  Some vendors
                    # (like Arrow) use the *manufacturer_part_name* as their
                    # *vendor_part_name*.  The data is in:
                    #     <span class="additional-value"> ... </span>:
                    vendor_part_name = manufacturer_part_name
                    for span1_tree in row_tree.find_all(
                      "span", class_="td-desc-distributor"):
                        # print(span1_tree.prettify())
                        for span2_tree in span1_tree.find_all(
                          "span", class_="additional-value"):
                            # Found it; grab it, encode it, and strip it:
                            vendor_part_name = span2_tree.get_text()

                    # The *stock* count is found as:
                    #    <td class="td-stock">stock</td>
                    stock = 0
                    stock_tree = row_tree.find("td", class_="td-stock")
                    if stock_tree is not None:
                        # Strip out commas, space, etc.:
                        stock_text = \
                          digits_only_re.sub("", stock_tree.get_text())
                        # Some sites do not report stock, and leave them
                        # empty.  We just leave *stock* as zero in this case:
                        if len(stock_text) != 0:
                            stock = min(int(stock_text), 100000000)
                        if tracing:
                            print(f"{tracing}stock_text='{stock_text}'")

                    # The *manufacturer_name* is found as:
                    #    <td class="td-mfg"><span>manufacturer_name</span></td>
                    manufacturer_name = ""
                    for mfg_name_tree in row_tree.find_all(
                      "td", class_="td-mfg"):
                        for span_tree in mfg_name_tree.find_all("span"):
                            # Found it; grab it, encode it, and strip it:
                            manufacturer_name = span_tree.get_text().strip()

                    # The *manufacturer_part_name* is found as:
                    #    <td class="td_part"><a ...>mfg_part_name</a></td>
                    manufacturer_part_name = ""
                    for mfg_part_tree in row_tree.find_all(
                      "td", class_="td-part"):
                        for a_tree in mfg_part_tree.find_all("a"):
                            # Found it; grab it, encode it, and strip it:
                            manufacturer_part_name = a_tree.get_text()

                    # The price breaks are encoded in a <ul> tree as follows:
                    #    <td class="td_price">
                    #       <ul>
                    #          <li>
                    #            <span class="label">quantity</span>
                    #            <span class="value">price</span>
                    #          </li>
                    #          ...
                    #       </ul>
                    #    </td>
                    price_breaks = []
                    price_list_tree = row_tree.find("td", class_="td-price")
                    if price_list_tree is not None:
                        for li_tree in price_list_tree.find_all("li"):
                            quantity_tree = li_tree.find("span", class_="label")
                            price_tree = li_tree.find("span", class_="value")
                            if quantity_tree is not None and price_tree is not None:
                                # We extract *quantity*:
                                quantity_text = digits_only_re.sub("", quantity_tree.get_text())
                                quantity = 1
                                if quantity_text != "":
                                    quantity = int(quantity_text)

                                # Extract *price* using only digits and '.':
                                price_text = ""
                                for character in price_tree.get_text():
                                    if character.isdigit() or character == ".":
                                        price_text += character
                                price = float(price_text)

                                # Look up the *exchange_rate* for *currency*:
                                exchange_rates = bom.ActualPart.ACTUAL_PART_EXCHANGE_RATES
                                if currency in exchange_rates:
                                    exchange_rate = exchange_rates[currency]
                                else:
                                    converter = CurrencyConverter()
                                    exchange_rate = converter.convert(1.0, currency, "USD")
                                    exchange_rates[currency] = exchange_rate

                                # Sometimes we get a bogus price of 0.0 and
                                # we just need to ignore the whole record:
                                if price > 0.0:
                                    price_break = bom.PriceBreak(
                                      quantity, price * exchange_rate)
                                    price_breaks.append(price_break)

                    # Now if we have an exact match on the *manufacturer_part_name*
                    # we can construct the *vendor_part* and append it to
                    # *vendor_parts*:
                    if original_manufacturer_part_name == manufacturer_part_name:
                        now = int(time.time())
                        vendor_part = bom.VendorPart(actual_part, vendor_name, vendor_part_name,
                                                     stock, price_breaks, now)
                        vendor_parts.append(vendor_part)

                        # Print stuff out if *trace* in enabled:
                        if tracing:
                            # Print everything out:
                            print(f"{tracing}vendor_name='{vendor_name}'")
                            print(f"{tracing}vendor_part_name='{vendor_part_name}'")
                            print(f"{tracing}manufacturer_part_name='{manufacturer_part_name}'")
                            print(f"{tracing}manufacturer_name='{manufacturer_name}'")
                            print(f"{tracing}stock={stock}")
                            price_breaks.sort()
                            for price_break in price_breaks:
                                price_text = "{0:.6f}".format(price_break.price)
                                print(f"{tracing}{price_break.quantity}: {price_text} ({currency})")

        # Wrap up any requested *tracing* and return the *vendor_parts*:
        vendor_parts_size = len(vendor_parts)
        print(f"Found {vendor_parts_size} vendors for '{manufacturer_part_name}' "
              f"for part '{search_name}'.")
        if tracing:
            print(f"{tracing}<=FindChips.lookup(*, '{actual_part.manufacturer_part_name}')"
                  f"=>[...](len={vendor_parts_size})")
        return vendor_parts


def panda_get(tracing=""):
    # Verify argument types:
    assert isinstance(tracing, str)

    # Create the *find_chips* object:
    find_chips = FindChips()
    return find_chips
