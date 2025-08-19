from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
import os
from RPA.Archive import Archive

@task
def order_robot_from_robotsparebin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=50)
    open_order_website()
    orders = get_orders()
    close_annoying_popup()
    for order in orders:
        fill_the_form(order)
        store_receipt_as_pdf(order['Order number'])
        order_another()
        close_annoying_popup()
    archive_pdfs()

def open_order_website():
    """Function to open the website to place the robot orders."""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    http = HTTP()
    tables = Tables()
    http.download(url='https://robotsparebinindustries.com/orders.csv',overwrite=True)
    table = tables.read_table_from_csv('orders.csv')
    return table

def close_annoying_popup():
    page = browser.page()
    page.click("text=OK")


def fill_the_form(order):
    page = browser.page()
    page.select_option("#head",order['Head'])
    page.check(f"input[name='body'][value='{order['Body']}']")
    page.fill("input[placeholder='Enter the part number for the legs']", order['Legs'])
    page.fill("#address", order['Address'])
    page.click("#preview") 
    while True:
        page.click("#order")
        if page.locator(".alert-danger").is_visible():
            continue
        else:
            break 

def order_another():
    page = browser.page()
    page.click("text=Order Another Robot")

def store_receipt_as_pdf(order_number):
    page = browser.page()
    pdf = PDF()
    os.makedirs("output", exist_ok=True)
    screenshot_robot_order(order_number)
    receipt_html = page.locator("#receipt").inner_html()
    pdf.html_to_pdf(receipt_html, f'output/{order_number}.pdf')
    pdf.add_files_to_pdf(
        files=[f'output/{order_number}.png'],
        target_document=f'output/{order_number}.pdf',append=True
    )

def screenshot_robot_order(order_number):
    page = browser.page()
    os.makedirs("output", exist_ok=True)
    page.locator("#robot-preview-image").screenshot(path=f'output/{order_number}.png')

def archive_pdfs():
    archive = Archive()
    archive.archive_folder_with_zip(
        folder = 'output',
        archive_name = 'output/orders.zip',
        include = "*pdf"
    )


