from flask import Flask, render_template, request, redirect, url_for
from peewee import *

db = SqliteDatabase('library.db')

class Book(Model):
    title = CharField()
    author = CharField()
    publication = CharField()
    pub_year = IntegerField()
    isbn = CharField()
    num_of_books = IntegerField()

    class Meta:
        database = db

class Member(Model):
    user_id = CharField()
    name = CharField()
    phone_no = CharField()

    class Meta:
        database = db

class IssueHistory(Model):
    user_id = ForeignKeyField(Member, backref='issues')
    isbn = ForeignKeyField(Book, backref='issues')
    issue_id = CharField()
    issue_date = DateField()
    return_date = DateField()
    current_status = TextField()

    class Meta:
        database = db

def initialize_db():
    db.connect()
    db.create_tables([Book, Member, IssueHistory], safe=True)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        Book.create(
            title=request.form['title'],
            author=request.form['author'],
            publication=request.form['publication'],
            pub_year=request.form['pub_year'],
            isbn=request.form['isbn'],
            num_of_books=request.form['num_of_books']
        )
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        Member.create(
            user_id=request.form['user_id'],
            name=request.form['name'],
            phone_no=request.form['phone_no']
        )
        return redirect(url_for('index'))
    return render_template('add_member.html')

@app.route('/allocate', methods=['GET', 'POST'])
def allocate():
    if request.method == 'POST':
        book = Book.get(Book.isbn == request.form['isbn'])
        member = Member.get(Member.user_id == request.form['user_id'])
        if book and member:
            IssueHistory.create(
                user_id=member,
                isbn=book,
                issue_id=request.form['issue_id'],
                issue_date=request.form['issue_date'],
                return_date=request.form['return_date'],
                current_status='issued'
            )
            book.num_of_books -= 1
            book.save()
            return redirect(url_for('index'))
    return render_template('allocate.html')

@app.route('/de_allocate', methods=['GET', 'POST'])
def de_allocate():
    if request.method == 'POST':
        issue = IssueHistory.get(IssueHistory.issue_id == request.form['issue_id'])
        if issue:
            book = Book.get(Book.isbn == issue.isbn)
            issue.current_status = 'returned'
            issue.save()
            book.num_of_books += 1
            book.save()
            return redirect(url_for('index'))
    return render_template('de_allocate.html')

@app.route('/remove_book', methods=['GET', 'POST'])
def remove_book():
    if request.method == 'POST':
        book = Book.get(Book.isbn == request.form['isbn'])
        if book:
            book.delete_instance()
            return redirect(url_for('index'))
    return render_template('remove_book.html')

@app.route('/remove_member', methods=['GET', 'POST'])
def remove_member():
    if request.method == 'POST':
        member = Member.get(Member.user_id == request.form['user_id'])
        if member:
            member.delete_instance()
            return redirect(url_for('index'))
    return render_template('remove_member.html')

if __name__ == '__main__':
    initialize_db()
    app.run(debug=True,port=5001)
