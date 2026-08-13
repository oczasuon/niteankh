"""Lightweight KH/EN translation dictionary. No build step, no compiled
.mo files — just a plain dict keyed by dotted string, looked up at request
time via the `t()` Jinja global (see app.py's context processor)."""

TRANSLATIONS = {
    # --- shared / nav / footer ---
    'nav.search_placeholder': {'km': 'ស្វែងរក...', 'en': 'Search...'},
    'nav.login': {'km': 'ចូលប្រើ', 'en': 'Login'},
    'nav.home': {'km': 'ទំព័រដើម', 'en': 'Home'},
    'nav.movies': {'km': 'ភាពយន្ត', 'en': 'Movies'},
    'nav.membership': {'km': 'សមាជិក', 'en': 'Membership'},
    'nav.wallet': {'km': 'កាបូប', 'en': 'Wallet'},
    'nav.profile': {'km': 'ប្រវត្តិរូប', 'en': 'Profile'},
    'footer.rights': {'km': 'រក្សាសិទ្ធិគ្រប់យ៉ាង។', 'en': 'All rights reserved.'},

    # --- admin shared layout ---
    'admin.nav.dashboard': {'km': 'ផ្ទាំងគ្រប់គ្រង', 'en': 'Dashboard'},
    'admin.nav.upload': {'km': 'បង្ហោះខ្លឹមសារ', 'en': 'Upload'},
    'admin.nav.manage': {'km': 'គ្រប់គ្រងខ្លឹមសារ', 'en': 'Manage'},
    'admin.nav.categories': {'km': 'ប្រភេទ', 'en': 'Categories'},
    'admin.nav.users': {'km': 'អ្នកប្រើប្រាស់', 'en': 'Users'},
    'admin.nav.reports': {'km': 'របាយការណ៍', 'en': 'Reports'},
    'admin.nav.settings': {'km': 'ការកំណត់', 'en': 'Settings'},
    'admin.nav.change_password': {'km': 'ប្តូរពាក្យសម្ងាត់', 'en': 'Change password'},
    'admin.nav.view_site': {'km': 'មើលគេហទំព័រ', 'en': 'View site'},
    'admin.nav.logout': {'km': 'ចាកចេញ', 'en': 'Logout'},

    # --- home page ---
    'home.trending': {'km': 'កំពុងពេញនិយម', 'en': 'Trending'},
    'home.watch_now': {'km': 'មើលឥឡូវ', 'en': 'Watch Now'},
    'home.all': {'km': 'ទាំងអស់', 'en': 'All'},
    'home.all_content': {'km': 'ខ្លឹមសារទាំងអស់', 'en': 'All Content'},
    'home.view_all': {'km': 'មើលទាំងអស់', 'en': 'View All'},

    # --- movies (browse) page ---
    'movies.title': {'km': 'ភាពយន្តទាំងអស់', 'en': 'All Movies'},
    'movies.total_count': {'km': 'សរុប', 'en': 'Total'},
    'movies.count_unit': {'km': 'រឿង', 'en': 'titles'},
    'movies.sort_popular': {'km': 'ពេញនិយម', 'en': 'Popular'},
    'movies.sort_newest': {'km': 'ថ្មីបំផុត', 'en': 'Newest'},
    'movies.sort_rating': {'km': 'ពិន្ទុខ្ពស់', 'en': 'Top Rated'},

    # --- shared movie card / episode unit ---
    'common.episodes_unit': {'km': 'ភាគ', 'en': 'eps'},
    'common.prev': {'km': 'ថយក្រោយ', 'en': 'Previous'},
    'common.next': {'km': 'មុខបន្ទាប់', 'en': 'Next'},

    # --- search page ---
    'search.title': {'km': 'លទ្ធផលស្វែងរក', 'en': 'Search Results'},
    'search.results_for': {'km': 'លទ្ធផលសម្រាប់', 'en': 'Results for'},
    'search.found': {'km': 'រកឃើញ', 'en': 'Found'},
    'search.results_unit': {'km': 'លទ្ធផល', 'en': 'results'},
    'search.no_results': {'km': 'មិនមានលទ្ធផលត្រូវនឹងការស្វែងរករបស់អ្នកទេ', 'en': 'No results match your search'},
    'search.try_other': {'km': 'សាកល្បងប្រើពាក្យគន្លឹះផ្សេង ឬជ្រើសរើសប្រភេទផ្សេង', 'en': 'Try different keywords or another category'},

    # --- watch page ---
    'watch.episode_label': {'km': 'ភាគ', 'en': 'Episode'},
    'watch.vip_only': {'km': 'មាតិកា VIP ប៉ុណ្ណោះ', 'en': 'VIP Content Only'},
    'watch.upgrade_vip': {'km': 'ដំឡើងកម្រិត VIP', 'en': 'Upgrade to VIP'},
    'watch.guest_register_prompt': {'km': 'សូមចុះឈ្មោះ ដើម្បីបន្តទស្សនា', 'en': 'Please register to keep watching'},
    'watch.guest_limit_message': {
        'km': 'អ្នកបានឈានដល់កម្រិតឥតគិតថ្លៃសម្រាប់ភ្ញៀវ (2 រឿង ឬ 8 នាទី) — ចុះឈ្មោះឥតគិតថ្លៃដើម្បីមើលបន្ត',
        'en': "You've reached the free guest limit (2 titles or 8 minutes) — sign up free to keep watching",
    },
    'watch.register_login': {'km': 'ចុះឈ្មោះ / ចូលប្រើ', 'en': 'Sign Up / Login'},
    'watch.added_to_list': {'km': 'បានបញ្ចូល', 'en': 'Added'},
    'watch.my_list': {'km': 'បញ្ជីរបស់ខ្ញុំ', 'en': 'My List'},
    'watch.episode_list': {'km': 'បញ្ជីភាគ', 'en': 'Episodes'},
    'watch.related': {'km': 'រឿងពាក់ព័ន្ធ', 'en': 'Related Titles'},

    # --- common form fields / buttons, reused across many pages ---
    'common.full_name': {'km': 'ឈ្មោះពេញ', 'en': 'Full Name'},
    'common.email': {'km': 'អ៊ីមែល', 'en': 'Email'},
    'common.phone': {'km': 'លេខទូរស័ព្ទ', 'en': 'Phone Number'},
    'common.sex': {'km': 'ភេទ', 'en': 'Gender'},
    'common.male': {'km': 'ប្រុស', 'en': 'Male'},
    'common.female': {'km': 'ស្រី', 'en': 'Female'},
    'common.other': {'km': 'ផ្សេងទៀត', 'en': 'Other'},
    'common.not_specified': {'km': 'មិនបញ្ជាក់', 'en': 'Not specified'},
    'common.dob': {'km': 'ថ្ងៃខែឆ្នាំកំណើត', 'en': 'Date of Birth'},
    'common.location': {'km': 'ទីតាំង', 'en': 'Location'},
    'common.save': {'km': 'រក្សាទុក', 'en': 'Save'},
    'common.cancel': {'km': 'បោះបង់', 'en': 'Cancel'},
    'common.current_password': {'km': 'ពាក្យសម្ងាត់បច្ចុប្បន្ន', 'en': 'Current Password'},
    'common.new_password': {'km': 'ពាក្យសម្ងាត់ថ្មី', 'en': 'New Password'},
    'common.confirm_new_password': {'km': 'បញ្ជាក់ពាក្យសម្ងាត់ថ្មី', 'en': 'Confirm New Password'},
    'common.min_6_chars': {'km': '(យ៉ាងតិច ៦ តួ)', 'en': '(min. 6 characters)'},
    'common.change_password': {'km': 'ប្តូរពាក្យសម្ងាត់', 'en': 'Change Password'},
    'common.logout': {'km': 'ចាកចេញពីគណនី', 'en': 'Log Out'},

    # --- profile page ---
    'profile.title': {'km': 'ប្រវត្តិរូប', 'en': 'Profile'},
    'profile.vip_member': {'km': 'សមាជិក VIP', 'en': 'VIP Member'},
    'profile.regular_member': {'km': 'សមាជិកទូទៅ', 'en': 'Regular Member'},
    'profile.my_list': {'km': 'បញ្ជីរបស់ខ្ញុំ', 'en': 'My List'},
    'profile.watched': {'km': 'មើលរួច', 'en': 'Watched'},
    'profile.renew_vip': {'km': 'បន្តសមាជិកភាព VIP', 'en': 'Renew VIP'},
    'profile.upgrade_vip': {'km': 'ដំឡើងកម្រិត VIP', 'en': 'Upgrade to VIP'},
    'profile.tab_settings': {'km': 'ការកំណត់គណនី', 'en': 'Account Settings'},
    'profile.empty_mylist': {'km': 'អ្នកមិនទាន់មានរឿងក្នុងបញ្ជីរបស់អ្នកទេ', 'en': "You don't have any titles in your list yet"},
    'profile.browse_movies': {'km': 'រកមើលរឿង', 'en': 'Browse Movies'},
    'profile.clear_history': {'km': 'សម្អាតប្រវត្តិ', 'en': 'Clear History'},
    'profile.empty_history': {'km': 'អ្នកមិនទាន់មានប្រវត្តិមើលទេ', 'en': "You don't have any watch history yet"},
    'profile.start_watching': {'km': 'ចាប់ផ្តើមមើល', 'en': 'Start Watching'},
    'profile.info_heading': {'km': 'ព័ត៌មានប្រវត្តិរូប', 'en': 'Profile Information'},

    # --- wallet page ---
    'common.coins_unit': {'km': 'កាក់', 'en': 'coins'},
    'wallet.balance_label': {'km': 'សមតុល្យកាបូបរបស់អ្នក', 'en': 'Your Wallet Balance'},
    'wallet.days_remaining_prefix': {'km': 'នៅសល់', 'en': ''},
    'wallet.days_remaining_suffix': {'km': 'ថ្ងៃទៀត', 'en': 'days remaining'},
    'wallet.not_vip_yet': {'km': 'មិនទាន់មានសិទ្ធិ VIP', 'en': 'Not a VIP member yet'},
    'wallet.topup_wallet': {'km': 'បញ្ចូលកាបូប', 'en': 'Top Up Wallet'},
    'wallet.topup_packages_heading': {'km': 'កញ្ចប់បញ្ចូលកាបូប', 'en': 'Top-up Packages'},
    'wallet.confirm_payment': {'km': 'បញ្ជាក់ការទូទាត់', 'en': 'Confirm Payment'},
    'wallet.scan_qr_heading': {'km': 'ស្កេន QR ដើម្បីទូទាត់', 'en': 'Scan QR to Pay'},
    'wallet.scan_instructions': {
        'km': 'ស្កេនតាមកម្មវិធីធនាគាររបស់អ្នក រួចបំពេញព័ត៌មានខាងក្រោមសម្រាប់ការត្រួតពិនិត្យ',
        'en': 'Scan using your banking app, then fill in the details below for verification',
    },
    'wallet.qr_not_set': {'km': 'Admin មិនទាន់បានកំណត់ QR ការទូទាត់ទេ', 'en': 'Admin has not set up a payment QR yet'},
    'wallet.bank_account_name_label': {'km': 'ឈ្មោះគណនីធនាគារ (អ្នកផ្ទេរ) *', 'en': 'Bank Account Name (Sender) *'},
    'wallet.bank_ref_label': {'km': 'លេខយោង / Hash ពីធនាគារ *', 'en': 'Reference / Hash from Bank *'},
    'wallet.payment_done': {'km': 'ខ្ញុំបានទូទាត់រួចរាល់', 'en': "I've Completed Payment"},
    'wallet.keep_receipt_note': {
        'km': 'សូមរក្សាទុករូបថតបញ្ជាក់ការទូទាត់ ក្នុងករណីត្រូវការផ្ទៀងផ្ទាត់',
        'en': 'Please keep a screenshot of your payment confirmation in case verification is needed',
    },
    'wallet.vip_membership_heading': {'km': 'សមាជិកភាព VIP', 'en': 'VIP Membership'},
    'wallet.buy_now': {'km': 'ទិញឥឡូវ', 'en': 'Buy Now'},
    'wallet.special_code_heading': {'km': 'កូដពិសេស', 'en': 'Redeem Code'},
    'wallet.enter_code_placeholder': {'km': 'បញ្ចូលកូដ...', 'en': 'Enter code...'},
    'wallet.use_code': {'km': 'ប្រើកូដ', 'en': 'Redeem'},
    'wallet.transaction_history_heading': {'km': 'ប្រវត្តិប្រតិបត្តិការ', 'en': 'Transaction History'},
    'wallet.no_transactions': {'km': 'មិនទាន់មានប្រតិបត្តិការទេ', 'en': 'No transactions yet'},
    'wallet.selected_package_js': {'km': 'កញ្ចប់ដែលបានជ្រើសរើស៖', 'en': 'Selected package:'},

    # --- membership page ---
    'membership.title': {'km': 'សមាជិក VIP', 'en': 'VIP Membership'},
    'membership.upgrade_to': {'km': 'ដំឡើងកម្រិតទៅជា', 'en': 'Upgrade to'},
    'membership.hero_desc': {
        'km': 'រីករាយជាមួយការមើលដោយគ្មានការរំខាន គុណភាព 4K ភាគថ្មីៗមុនគេ និងមាតិកាផ្តាច់មុខសម្រាប់សមាជិក VIP ប៉ុណ្ណោះ។',
        'en': 'Enjoy uninterrupted viewing, 4K quality, early access to new episodes, and exclusive content for VIP members only.',
    },
    'membership.you_are_vip': {'km': 'អ្នកគឺជាសមាជិក VIP', 'en': "You're a VIP Member"},
    'membership.you_are_regular': {'km': 'អ្នកគឺជាសមាជិកទូទៅ', 'en': "You're a Regular Member"},
    'membership.choose_plan_heading': {'km': 'ជ្រើសរើសគម្រោងសមាជិកភាព', 'en': 'Choose Your Plan'},
    'membership.select_this_plan': {'km': 'ជ្រើសរើសគម្រោងនេះ', 'en': 'Select This Plan'},
    'membership.payment_note_prefix': {'km': 'ការទូទាត់ប្រើប្រាស់សមតុល្យក្នុង', 'en': 'Payment uses the balance in your'},
    'membership.payment_note_suffix': {'km': 'របស់អ្នក', 'en': ''},
    'membership.benefits_heading': {'km': 'អត្ថប្រយោជន៍ VIP', 'en': 'VIP Benefits'},
    'membership.feature_col': {'km': 'មុខងារ', 'en': 'Feature'},
    'membership.free_col': {'km': 'ទូទៅ', 'en': 'Free'},
    'membership.faq_heading': {'km': 'សំណួរដែលសួរញឹកញាប់', 'en': 'Frequently Asked Questions'},

    'membership.feature.hd': {'km': 'មើលវីដេអូគុណភាព HD', 'en': 'Watch in HD quality'},
    'membership.feature.4k': {'km': 'មើលវីដេអូគុណភាព 4K', 'en': 'Watch in 4K quality'},
    'membership.feature.early_access': {'km': 'ភាគថ្មីៗចេញមុនគេ', 'en': 'Early access to new episodes'},
    'membership.feature.exclusive': {'km': 'មាតិកាផ្តាច់មុខ VIP ប៉ុណ្ណោះ', 'en': 'VIP-exclusive content'},
    'membership.feature.no_limit': {'km': 'គ្មានការកំណត់ចំនួនភាគក្នុងមួយថ្ងៃ', 'en': 'No daily episode limit'},
    'membership.feature.priority_support': {'km': 'ការគាំទ្រអតិថិជនអាទិភាព', 'en': 'Priority customer support'},
    'membership.feature.save_mylist': {'km': 'រក្សាទុកបញ្ជីរបស់ខ្ញុំ', 'en': 'Save your list'},

    'membership.faq.q1': {'km': 'តើខ្ញុំទូទាត់ថ្លៃសមាជិកភាព VIP យ៉ាងដូចម្តេច?', 'en': 'How do I pay for VIP membership?'},
    'membership.faq.a1': {
        'km': 'ការទូទាត់ប្រើប្រាស់សមតុល្យក្នុងកាបូបរបស់អ្នក។ សូមបញ្ចូលកាបូបជាមុននៅទំព័រកាបូប រួចត្រឡប់មកទំព័រនេះដើម្បីជ្រើសរើសគម្រោង។',
        'en': 'Payment uses the balance in your wallet. Top up your wallet first, then come back here to choose a plan.',
    },
    'membership.faq.q2': {'km': 'តើសមាជិកភាព VIP អាចបន្តដោយស្វ័យប្រវត្តិទេ?', 'en': 'Does VIP membership auto-renew?'},
    'membership.faq.a2': {
        'km': 'ទេ &mdash; សមាជិកភាព VIP មិនបន្តដោយស្វ័យប្រវត្តិទេ។ អ្នកអាចទិញបន្តនៅពេលណាក៏បាន ថ្ងៃដែលនៅសល់នឹងត្រូវបូកបន្ថែម។',
        'en': "No &mdash; VIP membership does not auto-renew. You can buy more anytime and remaining days will be added on top.",
    },
    'membership.faq.q3': {'km': 'តើខ្ញុំអាចប្រើគណនី VIP លើឧបករណ៍ច្រើនបានទេ?', 'en': 'Can I use my VIP account on multiple devices?'},
    'membership.faq.a3': {
        'km': 'បាទ/ចាស សមាជិក VIP អាចប្រើប្រាស់លើឧបករណ៍ច្រើនក្នុងពេលតែមួយ។',
        'en': 'Yes, VIP members can use their account on multiple devices.',
    },
    'membership.faq.q4': {'km': 'តើមានការសងប្រាក់ត្រឡប់ទេប្រសិនបើមិនពេញចិត្ត?', 'en': 'Is there a refund if I\'m not satisfied?'},
    'membership.faq.a4': {
        'km': 'កាក់ដែលបានទិញរួចមិនអាចដូរជាសាច់ប្រាក់វិញបានទេ ប៉ុន្តែនៅតែអាចប្រើសម្រាប់ទិញ VIP ឬសេវាកម្មផ្សេងទៀតបាន។',
        'en': 'Purchased coins cannot be converted back to cash, but they remain usable for VIP or other services.',
    },

    # --- login/signup page ---
    'login.title': {'km': 'ចូលប្រើ', 'en': 'Login'},
    'login.signup_tab': {'km': 'ចុះឈ្មោះ', 'en': 'Sign Up'},
    'common.password': {'km': 'ពាក្យសម្ងាត់', 'en': 'Password'},
    'common.your_name_placeholder': {'km': 'ឈ្មោះរបស់អ្នក', 'en': 'Your name'},
    'login.or_continue_with': {'km': 'ឬបន្តជាមួយ', 'en': 'Or continue with'},
    'login.continue_google': {'km': 'ចូលប្រើដោយ Google', 'en': 'Continue with Google'},
    'login.back_to_home': {'km': 'ត្រឡប់ទៅទំព័រដើម', 'en': 'Back to Home'},

    # --- admin login ---
    'admin.login.title': {'km': 'ចូលប្រើ Admin', 'en': 'Admin Login'},
    'admin.login.subtitle': {'km': 'ផ្ទាំងគ្រប់គ្រងខ្លឹមសារ', 'en': 'Content Management Panel'},
    'admin.login.back_to_site': {'km': 'ត្រឡប់ទៅគេហទំព័រ', 'en': 'Back to Site'},

    # --- admin change password ---
    'admin.change_password.subtitle': {'km': 'ប្តូរពាក្យសម្ងាត់សម្រាប់គណនីចូលប្រើផ្ទាំងគ្រប់គ្រងរបស់អ្នក', 'en': 'Change the password for your admin panel login'},

    # --- admin dashboard ---
    'admin.dashboard.subtitle': {'km': 'ទិដ្ឋភាពទូទៅនៃខ្លឹមសារនៅលើវេទិកា', 'en': 'Overview of content on the platform'},
    'admin.dashboard.total_content': {'km': 'ខ្លឹមសារសរុប', 'en': 'Total Content'},
    'admin.dashboard.admin_uploads': {'km': 'បង្ហោះដោយ Admin', 'en': 'Admin Uploads'},
    'admin.dashboard.categories': {'km': 'ប្រភេទ', 'en': 'Categories'},
    'admin.dashboard.upload_new': {'km': 'បង្ហោះខ្លឹមសារថ្មី', 'en': 'Upload New Content'},
    'admin.dashboard.manage_all': {'km': 'គ្រប់គ្រងខ្លឹមសារទាំងអស់', 'en': 'Manage All Content'},
    'admin.dashboard.recent_uploads': {'km': 'ខ្លឹមសារបង្ហោះថ្មីៗ', 'en': 'Recently Uploaded'},
    'admin.dashboard.no_uploads': {'km': 'មិនទាន់មានខ្លឹមសារបង្ហោះដោយ Admin ទេ', 'en': 'No admin-uploaded content yet'},
    'admin.dashboard.upload_now': {'km': 'បង្ហោះឥឡូវ', 'en': 'Upload Now'},

    # --- admin manage content ---
    'admin.manage.subtitle_total': {'km': 'សរុប', 'en': 'Total'},
    'admin.manage.content_unit': {'km': 'ខ្លឹមសារ', 'en': 'items'},
    'admin.manage.upload_new': {'km': 'បង្ហោះថ្មី', 'en': 'Upload New'},
    'admin.manage.filter_admin': {'km': 'បង្ហោះដោយ Admin', 'en': 'Admin Uploaded'},
    'admin.manage.search_placeholder': {'km': 'ស្វែងរកតាមចំណងជើង...', 'en': 'Search by title...'},
    'admin.manage.col_content': {'km': 'ខ្លឹមសារ', 'en': 'Content'},
    'admin.manage.col_category': {'km': 'ប្រភេទ', 'en': 'Category'},
    'admin.manage.col_episodes': {'km': 'ភាគ', 'en': 'Episodes'},
    'admin.manage.col_source': {'km': 'ប្រភព', 'en': 'Source'},
    'admin.manage.col_actions': {'km': 'សកម្មភាព', 'en': 'Actions'},
    'admin.manage.source_seeded': {'km': 'Seeded', 'en': 'Seeded'},
    'admin.manage.view': {'km': 'មើល', 'en': 'View'},
    'admin.manage.edit': {'km': 'កែសម្រួល', 'en': 'Edit'},
    'admin.manage.delete': {'km': 'លុប', 'en': 'Delete'},
    'admin.manage.delete_confirm': {'km': 'តើអ្នកប្រាកដថាចង់លុប', 'en': 'Are you sure you want to delete'},
    'admin.manage.locked_seeded': {'km': 'ខ្លឹមសារកសាងស្រាប់ មិនអាចកែបានទេ', 'en': 'Seeded content cannot be edited'},
    'admin.manage.no_results': {'km': 'មិនមានខ្លឹមសារត្រូវនឹងលក្ខខណ្ឌនេះទេ', 'en': 'No content matches this filter'},

    # --- admin categories ---
    'admin.categories.title': {'km': 'ប្រភេទខ្លឹមសារ', 'en': 'Content Categories'},
    'admin.categories.subtitle': {
        'km': 'គ្រប់គ្រងប្រភេទដែលបង្ហាញនៅពេលបង្ហោះខ្លឹមសារ និងជាតម្រងនៅលើគេហទំព័រ',
        'en': 'Manage categories shown when uploading content and as filters on the site',
    },
    'admin.categories.add_new': {'km': 'បន្ថែមប្រភេទថ្មី', 'en': 'Add New Category'},
    'admin.categories.add': {'km': 'បន្ថែម', 'en': 'Add'},
    'admin.categories.all_categories': {'km': 'ប្រភេទទាំងអស់', 'en': 'All Categories'},
    'admin.categories.content_unit': {'km': 'ខ្លឹមសារ', 'en': 'items'},
    'admin.categories.delete_confirm': {
        'km': 'លុបប្រភេទ',
        'en': 'Delete category',
    },
    'admin.categories.delete_confirm_suffix': {
        'km': 'មែនទេ? ខ្លឹមសារចាស់នឹងនៅតែមាន គ្រាន់តែលែងបង្ហាញក្នុងបញ្ជីជម្រើសទៀត',
        'en': '? Existing content keeps its category, it just stops appearing in the picker list',
    },
    'admin.categories.none_yet': {'km': 'មិនទាន់មានប្រភេទណាមួយទេ', 'en': 'No categories yet'},

    # --- admin users ---
    'admin.users.staff_accounts': {'km': 'គណនីបុគ្គលិក', 'en': 'Staff Accounts'},
    'admin.users.role_explainer': {
        'km': 'Admin មានសិទ្ធិពេញលេញ &bull; Poster មានសិទ្ធិតែបង្ហោះខ្លឹមសារប៉ុណ្ណោះ',
        'en': 'Admin has full access &bull; Poster can only upload content',
    },
    'admin.users.col_name': {'km': 'ឈ្មោះ', 'en': 'Name'},
    'admin.users.col_joined': {'km': 'ចូលរួម', 'en': 'Joined'},
    'admin.users.col_role': {'km': 'តួនាទី', 'en': 'Role'},
    'admin.users.col_actions': {'km': 'សកម្មភាព', 'en': 'Actions'},
    'admin.users.self_account': {'km': '(គណនីខ្លួនឯង)', 'en': '(your account)'},
    'admin.users.reset_password_title': {'km': 'កំណត់ពាក្យសម្ងាត់ថ្មី', 'en': 'Reset password'},
    'admin.users.reset_password_confirm': {'km': 'តើអ្នកប្រាកដថាចង់កំណត់ពាក្យសម្ងាត់ថ្មីសម្រាប់', 'en': 'Reset the password for'},
    'admin.users.revoke_staff_title': {'km': 'ដកសិទ្ធិបុគ្គលិក', 'en': 'Revoke staff access'},
    'admin.users.revoke_staff_confirm': {
        'km': 'តើអ្នកប្រាកដថាចង់ដកសិទ្ធិបុគ្គលិករបស់',
        'en': 'Revoke staff access for',
    },
    'admin.users.revoke_staff_confirm_suffix': {
        'km': 'មែនទេ? (គណនីនឹងក្លាយជាអតិថិជនធម្មតា)',
        'en': '? (account becomes a regular client)',
    },
    'admin.users.add_staff_heading': {'km': 'បន្ថែមគណនីបុគ្គលិកថ្មី', 'en': 'Add New Staff Account'},
    'admin.users.name_placeholder': {'km': 'ឈ្មោះ', 'en': 'Name'},
    'admin.users.email_placeholder': {'km': 'អ៊ីមែល', 'en': 'Email'},
    'admin.users.all_clients': {'km': 'អតិថិជនទាំងអស់', 'en': 'All Clients'},
    'admin.users.total_users': {'km': 'សរុប', 'en': 'Total'},
    'admin.users.users_unit': {'km': 'អ្នកប្រើប្រាស់', 'en': 'users'},
    'admin.users.search_client_placeholder': {'km': 'ស្វែងរកតាមឈ្មោះ ឬ អ៊ីមែល...', 'en': 'Search by name or email...'},
    'admin.users.col_coins': {'km': 'កាក់', 'en': 'Coins'},
    'admin.users.no_clients': {'km': 'មិនមានអតិថិជនត្រូវនឹងលក្ខខណ្ឌនេះទេ', 'en': 'No clients match this filter'},

    # --- admin reports ---
    'admin.reports.subtitle': {'km': 'សង្ខេបអ្នកប្រើប្រាស់ ខ្លឹមសារ និងលំហូរសាច់ប្រាក់', 'en': 'Summary of users, content, and cash flow'},
    'admin.reports.overview': {'km': 'ទិដ្ឋភាពទូទៅ', 'en': 'Overview'},
    'admin.reports.total_users': {'km': 'អ្នកប្រើប្រាស់សរុប', 'en': 'Total Users'},
    'admin.reports.total_content': {'km': 'ខ្លឹមសារសរុប', 'en': 'Total Content'},
    'admin.reports.current_balance': {'km': 'សមតុល្យសរុបបច្ចុប្បន្ន', 'en': 'Current Total Balance'},
    'admin.reports.active_vip': {'km': 'សមាជិក VIP សកម្ម', 'en': 'Active VIP Members'},
    'admin.reports.cashflow_heading': {'km': 'លំហូរសាច់ប្រាក់ (គិតជាកាក់)', 'en': 'Cash Flow (in coins)'},
    'admin.reports.total_topped_up': {'km': 'សរុបបញ្ចូលកាបូប (Top-up + កូដ)', 'en': 'Total Topped Up (Top-up + Codes)'},
    'admin.reports.total_spent': {'km': 'សរុបចំណាយទិញ VIP / មាតិកា', 'en': 'Total Spent on VIP / Content'},
    'admin.reports.users_by_account': {'km': 'អ្នកប្រើប្រាស់ តាមគណនី', 'en': 'Users by Account'},
    'admin.reports.accounts_unit': {'km': 'គណនី', 'en': 'accounts'},
    'admin.reports.col_user': {'km': 'អ្នកប្រើប្រាស់', 'en': 'User'},
    'admin.reports.col_joined': {'km': 'ចូលរួមនៅ', 'en': 'Joined'},
    'admin.reports.col_balance': {'km': 'សមតុល្យ', 'en': 'Balance'},
    'admin.reports.col_total_topup': {'km': 'សរុបបញ្ចូល', 'en': 'Total Topped Up'},
    'admin.reports.col_total_spent': {'km': 'សរុបចំណាយ', 'en': 'Total Spent'},
    'admin.reports.no_users': {'km': 'មិនទាន់មានអ្នកប្រើប្រាស់ចុះឈ្មោះនៅឡើយទេ', 'en': 'No registered users yet'},
    'admin.reports.content_by_category': {'km': 'ខ្លឹមសារតាមប្រភេទ', 'en': 'Content by Category'},
    'admin.reports.seeded_content': {'km': 'ខ្លឹមសារកសាងស្រាប់ (Seeded)', 'en': 'Seeded Content'},
    'admin.reports.admin_uploaded': {'km': 'បង្ហោះដោយ Admin', 'en': 'Admin Uploaded'},

    # --- admin settings ---
    'admin.settings.subtitle': {'km': 'គ្រប់គ្រងព័ត៌មានទូទាត់ដែលបង្ហាញនៅទំព័រកាបូប', 'en': 'Manage the payment info shown on the wallet page'},
    'admin.settings.qr_heading': {'km': 'QR ការទូទាត់ (KHQR)', 'en': 'Payment QR (KHQR)'},
    'admin.settings.qr_subtitle': {
        'km': 'រូបភាពនេះនឹងបង្ហាញនៅក្នុងផ្ទាំង "បញ្ជាក់ការទូទាត់" នៅទំព័រកាបូបសម្រាប់អ្នកប្រើប្រាស់ទាំងអស់',
        'en': 'This image is shown in the "Confirm Payment" panel on the wallet page for all users',
    },
    'admin.settings.currently_using_qr': {'km': 'កំពុងប្រើប្រាស់ QR នេះ', 'en': 'Currently using this QR'},
    'admin.settings.upload_to_replace': {'km': 'ផ្ទុកឡើងជំនួសរូបភាពខាងក្រោមដើម្បីប្តូរ', 'en': 'Upload below to replace it'},
    'admin.settings.no_qr_set': {
        'km': 'មិនទាន់មាន QR ការទូទាត់ត្រូវបានកំណត់ទេ &mdash; អ្នកប្រើប្រាស់នឹងឃើញកន្លែងទំនេរ',
        'en': 'No payment QR has been set yet &mdash; users will see an empty space',
    },
    'admin.settings.upload_new_qr': {'km': 'ផ្ទុករូបភាព QR ថ្មី', 'en': 'Upload New QR Image'},
    'admin.settings.file_types': {'km': 'JPG, PNG, WEBP ឬ GIF', 'en': 'JPG, PNG, WEBP or GIF'},
    'admin.settings.backfill_heading': {'km': 'ស្កេនប្រតិបត្តិការចាស់', 'en': 'Scan Old Transactions'},
    'admin.settings.backfill_subtitle': {
        'km': 'ស្កេនរកសារចាស់ៗក្នុងក្រុម Telegram ដែលមិនទាន់បានចាប់យក (ឧ. សារដែលផ្ញើមុនពេល userbot ភ្ជាប់) ហើយរក្សាទុកប្រតិបត្តិការណាមួយថ្មីៗ',
        'en': 'Scans old messages in the Telegram group that were not yet captured (e.g. sent before the userbot connected) and stores any new transactions',
    },
    'admin.settings.scan_now': {'km': 'ស្កេនឥឡូវ', 'en': 'Scan Now'},

    # --- admin upload ---
    'admin.upload.edit_title': {'km': 'កែសម្រួលខ្លឹមសារ', 'en': 'Edit Content'},
    'admin.upload.new_title': {'km': 'បង្ហោះខ្លឹមសារវីដេអូថ្មី', 'en': 'Upload New Video Content'},
    'admin.upload.subtitle': {
        'km': 'ខ្លឹមសារនេះនឹងបង្ហាញភ្លាមៗនៅលើទំព័រដើម ការស្វែងរក និងទំព័រភាពយន្ត',
        'en': 'This content will appear immediately on the home page, search, and movies page',
    },
    'admin.upload.title_label': {'km': 'ចំណងជើងរឿង *', 'en': 'Title *'},
    'admin.upload.category_label': {'km': 'ប្រភេទ *', 'en': 'Category *'},
    'admin.upload.quality_label': {'km': 'គុណភាព', 'en': 'Quality'},
    'admin.upload.total_episodes_label': {'km': 'ចំនួនភាគ *', 'en': 'Total Episodes *'},
    'admin.upload.year_label': {'km': 'ឆ្នាំ', 'en': 'Year'},
    'admin.upload.rating_label': {'km': 'ពិន្ទុ (0-10)', 'en': 'Rating (0-10)'},
    'admin.upload.video_file_label': {'km': 'ឯកសារវីដេអូ', 'en': 'Video File'},
    'admin.upload.current_video': {'km': 'វីដេអូបច្ចុប្បន្ន៖', 'en': 'Current video:'},
    'admin.upload.video_replace_note': {'km': 'ជ្រើសរើសឯកសារថ្មីដើម្បីជំនួស ឬទុកទទេដើម្បីរក្សាវីដេអូដដែល', 'en': 'Choose a new file to replace it, or leave blank to keep the current one'},
    'admin.upload.or': {'km': 'ឬ', 'en': 'or'},
    'admin.upload.embed_url_label': {'km': 'តំណ Embed (YouTube, Google Drive, Vimeo, ...)', 'en': 'Embed URL (YouTube, Google Drive, Vimeo, ...)'},
    'admin.upload.embed_note': {
        'km': 'ភ្ជាប់តំណភាគច្រើនផ្លាស់ប្តូរស្វ័យប្រវត្តិទៅជា Embed &mdash; ការផ្ទុកឯកសារខាងលើ និងតំណ Embed ជ្រើសរើសយកតែមួយ (ការផ្ទុកឯកសារថ្មីជំនួសតំណ Embed ចាស់ និងផ្ទុយមកវិញ)',
        'en': 'Most links auto-convert to an embed &mdash; the file upload above and this embed link are mutually exclusive (uploading a new file replaces an existing embed link, and vice versa)',
    },
    'admin.upload.thumbnail_label': {'km': 'រូបភាព Thumbnail (ស្រេចចិត្ត)', 'en': 'Thumbnail Image (optional)'},
    'admin.upload.thumbnail_note': {'km': 'ប្រសិនបើមិនបញ្ចូលរូបភាព ប្រព័ន្ធនឹងប្រើពណ៌ខាងក្រោមជំនួសវិញ', 'en': "If no image is provided, the color below will be used instead"},
    'admin.upload.remove': {'km': 'យកចេញ', 'en': 'Remove'},
    'admin.upload.color_label': {'km': 'ពណ៌ជំនួស (ប្រើនៅពេលគ្មានរូបភាព Thumbnail)', 'en': 'Fallback Color (used when there is no thumbnail)'},
    'admin.upload.description_label': {'km': 'ការពិពណ៌នា', 'en': 'Description'},
    'admin.upload.description_placeholder': {'km': 'សេចក្តីសង្ខេបរឿង...', 'en': 'Synopsis...'},
    'admin.upload.vip_only_checkbox': {'km': 'កំណត់ជាមាតិកា VIP ប៉ុណ្ណោះ', 'en': 'Mark as VIP-only content'},
    'admin.upload.featured_checkbox': {'km': 'បង្ហាញនៅក្នុង Slide ទំព័រដើម (Hero Slider)', 'en': 'Show in the home page Hero Slider'},
    'admin.upload.slide_image_label': {'km': 'រូបភាព Slide (Hero Banner) *', 'en': 'Slide Image (Hero Banner) *'},
    'admin.upload.slide_image_note': {'km': 'រូបភាពទទឹង (ឧ. 1600&times;600) សម្រាប់បង្ហាញនៅលើ Banner ធំក្នុងទំព័រដើម', 'en': 'A wide image (e.g. 1600&times;600) shown on the large home page banner'},
    'admin.upload.slide_replace_note': {'km': 'ជ្រើសរើសរូបភាពថ្មីដើម្បីជំនួស ឬទុកទទេដើម្បីរក្សារូបភាពដដែល', 'en': 'Choose a new image to replace it, or leave blank to keep the current one'},
    'admin.upload.save_changes': {'km': 'រក្សាទុកការផ្លាស់ប្តូរ', 'en': 'Save Changes'},
    'admin.upload.publish': {'km': 'បង្ហោះខ្លឹមសារ', 'en': 'Publish Content'},
    'admin.upload.editing_now': {'km': 'កំពុងកែសម្រួល', 'en': 'Now editing'},
    'admin.upload.view_on_site': {'km': 'មើលនៅគេហទំព័រ', 'en': 'View on site'},
    'admin.upload.manage_content': {'km': 'គ្រប់គ្រងខ្លឹមសារ', 'en': 'Manage content'},
    'admin.upload.manage_episodes_heading': {'km': 'គ្រប់គ្រងវីដេអូតាមភាគ', 'en': 'Manage Videos by Episode'},
    'admin.upload.episodes_unit': {'km': 'ភាគ', 'en': 'episodes'},
    'admin.upload.ep1_note': {
        'km': 'ភាគទី ០១ ប្រើវីដេអូដែលបានផ្ទុកខាងលើរួចហើយ (កែវីដេអូភាគទី ០១ បាននៅផ្នែក "ឯកសារវីដេអូ" ខាងលើ)',
        'en': 'Episode 01 uses the video already uploaded above (edit episode 01\'s video in the "Video File" section above)',
    },
    'admin.upload.ep_pending_note': {
        'km': 'ភាគខាងក្រោមមិនទាន់មានវីដេអូផ្ទាល់ខ្លួន នឹងប្រើវីដេអូខាងលើដដែលរហូតដល់អ្នកផ្ទុកឲ្យវា',
        'en': "Episodes below without their own video will use the main video above until you upload one",
    },
    'admin.upload.has_video': {'km': 'មានវីដេអូ', 'en': 'Has video'},
    'admin.upload.has_embed': {'km': 'មានតំណ Embed', 'en': 'Has embed link'},
    'admin.upload.uses_main_video': {'km': 'ប្រើវីដេអូចម្បង', 'en': 'Uses main video'},
    'admin.upload.upload_btn': {'km': 'ផ្ទុក', 'en': 'Upload'},
    'admin.upload.embed_placeholder': {'km': 'ឬតំណ Embed (YouTube, Drive, ...)', 'en': 'Or embed URL (YouTube, Drive, ...)'},
    'admin.upload.delete_ep_confirm': {'km': 'លុបវីដេអូភាគ', 'en': 'Delete video for episode'},
}


def t(key, lang='km'):
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get('km') or key
