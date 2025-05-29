from app import create_app, db
from app.models import User, Role

app = create_app()

with app.app_context():

    def get_or_create_role(name, description):
        role = Role.query.filter_by(name=name).first()
        if not role:
            role = Role(name=name, description=description)
            db.session.add(role)
            db.session.commit()
        return role

    role_user = get_or_create_role('пользователь', 'Обычный пользователь')
    role_admin = get_or_create_role('администратор', 'Администратор системы')
    role_moderator = get_or_create_role('модератор', 'Модератор контента')

    users_data = [
        {
            'login': 'testuser',
            'last_name': 'Косарева',
            'first_name': 'Светлана',
            'middle_name': 'Александровна',
            'role': role_user,
            'password': 'qwerty123'
        },
        {
            'login': 'adminuser',
            'last_name': 'Петров',
            'first_name': 'Игорь',
            'middle_name': 'Сергеевич',
            'role': role_admin,
            'password': 'adminpass'
        },
        {
            'login': 'moderatoruser',
            'last_name': 'Сидорова',
            'first_name': 'Ольга',
            'middle_name': 'Николаевна',
            'role': role_moderator,
            'password': 'moderpass'
        }
    ]

    for udata in users_data:
        user = User.query.filter_by(login=udata['login']).first()
        if not user:
            user = User(
                login=udata['login'],
                last_name=udata['last_name'],
                first_name=udata['first_name'],
                middle_name=udata['middle_name'],
                role=udata['role']
            )
            user.set_password(udata['password'])
            db.session.add(user)

    db.session.commit()
    print("Пользователи успешно созданы или уже существуют.")
