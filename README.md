<div align="center">
    <img src="https://frappecloud.com/files/pos.png" height="128">
    <h2>POS AWESOME</h2>
</div>

#### An advanced Point of Sale system for [Erpnext](https://github.com/frappe/erpnext) built with [Vue.js](https://github.com/vuejs/vue) and [Vuetify](https://github.com/vuetifyjs/vuetify)

---

## App Summary

POS Awesome is a modern, feature-rich Point of Sale application for ERPNext that enhances the retail experience. The application is designed with speed, usability, and flexibility in mind to meet various retail business needs.

### App Structure
- **Frontend**: Built with Vue.js 3 and Vuetify 3 for a responsive and interactive UI
- **Backend**: Integrated with Frappe/ERPNext for seamless data management
- **API Layer**: RESTful API endpoints for communication between frontend and backend

### App Logic
The application follows a client-server architecture where:
1. The Vue.js frontend handles the user interface and interactions
2. API calls connect to ERPNext backend for data operations
3. Real-time updates ensure accurate inventory and transaction information
4. Modular design allows for easy customization and extension

### Key Features
- Dual view modes (list and card) with item images
- Advanced payment handling (credit sales, loyalty points, mobile payments)
- Comprehensive inventory management (batch/serial tracking, variants)
- Returns processing and credit note management
- Multiple language support and shortcut keys for efficiency

---

### How to Install

#### Self Hosting:

1. `bench get-app posawesome https://github.com/abdopcnet/posawesome_andalus.git`
2. `bench setup requirements`
3. `bench build --app posawesome`
4. `bench restart`
5. `bench --site [your.site.name] install-app posawesome`
6. `bench --site [your.site.name] migrate`

---

### Support

#### Technical Support:

For support inquiries, please email [abdopcnet@gmail.com](mailto:abdopcnet@gmail.com)

#### Bug Reports and Feature Requests:

Please create GitHub issues on our repository:
[https://github.com/abdopcnet/posawesome_andalus/issues](https://github.com/abdopcnet/posawesome_andalus/issues)

---

### How To Use:

[POS Awesome Wiki](https://github.com/abdopcnet/posawesome_andalus/wiki)

---

### Shortcuts:

- `CTRL or CMD + S` open payments
- `CTRL or CMD + X` submit payments
- `CTRL or CMD + D` remove first item from the top
- `CTRL or CMD + A` expand first item from the top
- `CTRL or CMD + E` focus on discount field

---

### Requirements & Dependencies

#### Backend
- [Frappe](https://github.com/frappe/frappe) - Core framework
- [Erpnext](https://github.com/frappe/erpnext) - ERP system

#### Frontend
- [Vue.js](https://github.com/vuejs/vue) (v3.5+) - Progressive JavaScript framework
- [Vuetify](https://github.com/vuetifyjs/vuetify) (v3.6+) - Material design component framework
- [Lodash](https://lodash.com/) (v4.17+) - JavaScript utility library
- [Mitt](https://github.com/developit/mitt) (v3.0+) - Event emitter/pubsub

---

### App Information

- **Publisher**: future-support
- **Description**: Modern Point of Sale system for ERPNext
- **Contact**: abdopcnet@gmail.com
- **License**: GPLv3
- **Repository**: [https://github.com/abdopcnet/posawesome_andalus.git](https://github.com/abdopcnet/posawesome_andalus.git)

---

### Contributing

Please follow the ERPNext contribution guidelines:

1. [Issue Guidelines](https://github.com/frappe/erpnext/wiki/Issue-Guidelines)
2. [Pull Request Requirements](https://github.com/frappe/erpnext/wiki/Contribution-Guidelines)

---

### License

GNU/General Public License v3 (GPLv3)
