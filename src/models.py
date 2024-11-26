class PageData:
    def __init__(self, page_number):
        self.page_number = page_number  # Sets self.page_number to page_number
        self.forms = []  # Initializes self.forms as an empty list
        self.tables = []  # Initializes self.tables as an empty list

    def add_form_data(self, form_data):
        self.forms.append(form_data)  # Appends form_data (a dictionary) to self.forms

    def add_table_data(self, table_data):
        self.tables.append(
            table_data
        )  # Appends table_data (a dictionary) to self.tables
