class Soldtableclean:
    def __init__(self, productentry):
        self.word_list = None
        self.productentry = str(productentry)

    def organize_data(self, group_size):
        result = []

        for i in range(0, len(self.word_list), group_size):
            sublist = self.word_list[i:i + group_size]
            result.append(sublist)

        return result

    def str_to_list(self):
        self.word_list = self.productentry.split()
        result = self.organize_data(5)
        return result


class Setdatabase:
    def __init__(self, record):
        self.list = record

    def list_of_item(self):
        itemlist = []
        for item in self.list:
            itemlist.append(item[0])
        return itemlist

    def list_of_quantities(self):
        quantities = []
        for item in self.list:
            # Check if item is a list and has at least 3 elements
            if isinstance(item, list) and len(item) > 2:
                quantities.append(item[2])
            else:
                # Handle the case where item is not a list or doesn't have index 2
                quantities.append(None)
        return quantities
