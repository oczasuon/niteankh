"""Seeds the database with the same 120-title mock catalog used by the original
static site (niteankhv2/movies-data.js), plus a demo admin account and a demo
regular account so the app is usable immediately after setup."""

from app import create_app
from models import Category, Movie, User, db

CATEGORIES = ['រឿងភាគចិន', 'រឿងភាគកូរ៉េ', 'រឿងហូលីវូដ', 'រឿងភាគថៃ', 'រឿងភាគខ្មែរ', 'រឿងតុក្កតា']

TITLES = [
    'នាងត្រកួន', 'ចិត្តអាក្រក់', 'វាសនាអ្នកក្រ', 'សេចក្តីស្នេហា', 'ម្ដាយក្មេកចិត្តជា', 'កូនប្រសារស្រី',
    'ស្ដេចភ្នំអាថ៌កំបាំង', 'យុទ្ធសាស្ត្រប្រយុទ្ធ', 'កោះអាថ៌កំបាំង', 'ដំណើរផ្សងព្រេង', 'ទីក្រុងមន្តអាគម', 'ខ្លាឃ្មុំនិងមិត្ត',
    'បណ្ដាសាស្នេហ៍', 'ចិត្តព្រៃផ្សៃ', 'វាសនាឧត្ដម', 'ប្រពន្ធដើម', 'កូនបំណុល', 'ស្រមោលអតីតកាល',
]

GRADIENTS = [
    'from-teal-800 via-purple-900 to-rose-900',
    'from-blue-900 via-indigo-900 to-slate-900',
    'from-emerald-900 via-teal-900 to-cyan-950',
    'from-red-950 via-rose-900 to-amber-950',
    'from-purple-950 via-violet-900 to-fuchsia-950',
    'from-yellow-900 via-amber-900 to-orange-950',
]

DESCRIPTIONS = [
    'រឿងរ៉ាវអាថ៌កំបាំងអំពីព្រឹត្តិការណ៍ចម្លែកៗ ដែលកើតឡើងនៅក្នុងភូមិដាច់ស្រយាលមួយ បង្កឡើងដោយបណ្ដាសាពីបុរាណកាល។ តួឯកត្រូវប្រឈមមុខនឹងការសាកល្បងជាច្រើន ដើម្បីរកឃើញការពិត និងសង្គ្រោះគ្រួសាររបស់ខ្លួន។',
    'ដំណើររឿងរបស់គ្រួសារមួយ ដែលត្រូវប្រយុទ្ធជាមួយវាសនា និងឧបសគ្គជីវិត ក្នុងសង្គមដែលពោរពេញទៅដោយការប្រកួតប្រជែង។ សេចក្តីស្រលាញ់ និងភាពស្មោះត្រង់ គឺជាកូនសោនៃជោគជ័យ។',
    'នៅពេលដែលអតីតកាលវិលត្រឡប់មកវិញ តួឯកត្រូវជ្រើសរើសរវាងសេចក្តីស្រលាញ់ និងកាតព្វកិច្ច។ រឿងនេះនឹងនាំអ្នកទស្សនាឆ្លងកាត់អារម្មណ៍ជាច្រើនរូបភាព។',
]

TOTAL_ITEMS = 120
EPISODES_PER_ITEM = 12


def build_movies():
    movies = []
    for i in range(TOTAL_ITEMS):
        title = TITLES[i % len(TITLES)]
        category = CATEGORIES[i % len(CATEGORIES)]
        rating = round(7 + (i % 30) / 10, 1)
        year = 2020 + (i % 6)
        movies.append(Movie(
            title=f'រឿង {title}',
            category=category,
            description=DESCRIPTIONS[i % len(DESCRIPTIONS)],
            total_episodes=EPISODES_PER_ITEM,
            quality='4K' if i % 3 == 0 else 'FHD',
            year=year,
            rating=rating,
            vip=(i % 4 == 0),
            bg_grad=GRADIENTS[i % len(GRADIENTS)],
            is_admin_upload=False,
        ))
    return movies


def run():
    app = create_app()
    with app.app_context():
        db.create_all()

        existing_categories = {c.name for c in Category.query.all()}
        new_categories = [Category(name=name) for name in CATEGORIES if name not in existing_categories]
        if new_categories:
            db.session.bulk_save_objects(new_categories)
            db.session.commit()
            print(f'Seeded {len(new_categories)} categories.')

        if Movie.query.count() == 0:
            db.session.bulk_save_objects(build_movies())
            db.session.commit()
            print(f'Seeded {TOTAL_ITEMS} movies.')
        else:
            print('Movies already seeded, skipping.')

        if not User.query.filter_by(email='admin@niteankh.local').first():
            admin = User(name='Admin', email='admin@niteankh.local', is_admin=True)
            admin.set_password('admin123')
            db.session.add(admin)
            print('Created admin account: admin@niteankh.local / admin123')

        if not User.query.filter_by(email='demo@niteankh.local').first():
            demo = User(name='អ្នកប្រើប្រាស់សាកល្បង', email='demo@niteankh.local', balance=1000)
            demo.set_password('demo1234')
            db.session.add(demo)
            print('Created demo account: demo@niteankh.local / demo1234 (1000 coins)')

        db.session.commit()


if __name__ == '__main__':
    run()
