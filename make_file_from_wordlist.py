"""
Meant to be run from the silverlantern directory

We're going to take the wordlist we lifted from the
aspell project and load it into the DB. To do that,
we need to create a SQL file.
"""

#from public.models import Word
import gzip

#LINE_TEMPLATE = "INSERT INTO public_word (first_name, last_name) "\
#VALUES ('John', 'Lennon');"
#LINE_TEMPLATE = "INSERT INTO public_word (word) VALUES ('%s');\n"

TEMPLATE = """ {
    "model": "public.Word",
    "pk": %d,
    "fields": {"word": "%s"}
 }"""


def main():
    counter = 0
    section = ['', '']
    with open("public/fixtures/word.json", 'w') as output_file:
        with gzip.open("en-common.wl.gz", 'rb') as input_file:
            input_line = "START"
            output_file.write('[\n')
            while input_line:
                counter += 1
                input_line = input_file.readline().strip()
                if section[1] and input_line != '':
                    output_file.write(section[1] + ',\n')
                section[1] = section[0]
                section[0] = TEMPLATE % (counter, input_line)
            output_file.write(section[1] + '\n')
            output_file.write(']\n')


if __name__ == "__main__":
    main()
