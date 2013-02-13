"""
Meant to be run from the silverlantern directory

We're going to take the wordlist we lifted from the
aspell project and load it into the DB. To do that,
we need to create a SQL file.
"""

from public.models import Word
import gzip

#LINE_TEMPLATE = "INSERT INTO public_word (first_name, last_name) "\
#VALUES ('John', 'Lennon');"
#LINE_TEMPLATE = "INSERT INTO public_word (word) VALUES ('%s');\n"


def main():
    if 1 == 1:
    #with open("public/sql/words.sql", 'w') as output_file:
        with gzip.open("en-common.wl.gz", 'rb') as input_file:
            input_line = "START"
            while input_line:
                input_line = input_file.readline().strip()
                if "'" in input_line:
                    input_line = input_line.replace("'", "''")
                print ">>", input_line
                new_word = Word(word=input_line)
                new_word.save()
                #output_file.write(LINE_TEMPLATE % input_line)


if __name__ == "__main__":
    main()
