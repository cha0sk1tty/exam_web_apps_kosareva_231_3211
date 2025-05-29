from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    SelectMultipleField,
    FileField,
    PasswordField,
    SubmitField,
    BooleanField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    IntegerField,
    SelectMultipleField,
    FileField,
    SubmitField,
    SelectField,
)
from wtforms.validators import DataRequired, Length, NumberRange, InputRequired


class BookForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Описание", validators=[DataRequired()])
    year = IntegerField(
        "Год", validators=[DataRequired(), NumberRange(min=1000, max=9999)]
    )
    publisher = StringField("Издатель", validators=[DataRequired(), Length(max=150)])
    author = StringField("Автор", validators=[DataRequired(), Length(max=150)])
    pages = IntegerField(
        "Количество страниц", validators=[DataRequired(), NumberRange(min=1)]
    )
    genres = SelectMultipleField("Жанры", coerce=int, validators=[DataRequired()])
    cover = FileField("Обложка")
    submit = SubmitField("Сохранить")


class ReviewForm(FlaskForm):
    rating = SelectField(
        "Оценка",
        choices=[
            (5, "Отлично"),
            (4, "Хорошо"),
            (3, "Удовлетворительно"),
            (2, "Неудовлетворительно"),
            (1, "Плохо"),
            (0, "Ужасно"),
        ],
        default=5,
        coerce=int,
    )
    text = TextAreaField(
        "Текст рецензии", validators=[InputRequired(), Length(min=10, max=2000)]
    )


class LoginForm(FlaskForm):
    login = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class SearchForm(FlaskForm):
    title = StringField('Название', validators=[Optional()])
    genres = SelectMultipleField('Жанр', coerce=int, validators=[Optional()])
    years = SelectMultipleField('Год', coerce=int, validators=[Optional()])
    pages_min = IntegerField('Объём от', validators=[Optional()])
    pages_max = IntegerField('Объём до', validators=[Optional()])
    author = StringField('Автор', validators=[Optional()])
    submit = SubmitField('Найти')
    class Meta:
        csrf = False 
    