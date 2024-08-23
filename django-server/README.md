# django-server

## Django Database ORM

### Foreign Key contraint names
When using `models.ForeignKey`, the constraint name generated by django contains some kind of hash:

`polls_choice_question_id_c5b4b260_fk_polls_question_id` 

No clue on what `c5b4b260` is supposed to be.

https://docs.djangoproject.com/en/5.1/ref/models/fields/#django.db.models.ForeignKey says nothing about it.

The only thing I found out while searching for a way to control this naming was (however not useful):
https://stackoverflow.com/questions/66144560/django-mssql-override-foreign-key-constraint-name-generation