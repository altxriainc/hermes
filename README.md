
# Hermes ORM

![Latest Version](https://img.shields.io/github/v/release/altxriainc/hermes)
![GitHub stars](https://img.shields.io/github/stars/altxriainc/hermes?style=social)
![GitHub forks](https://img.shields.io/github/forks/altxriainc/hermes?style=social)
![GitHub license](https://img.shields.io/github/license/altxriainc/hermes)

**Hermes ORM** is a modern Python ORM designed for simplicity, flexibility, and performance. With support for relational mappings, migrations, and advanced querying, Hermes ORM is tailored for developers who need a powerful yet intuitive tool for managing database operations in their applications.

---

## 🚀 Key Features

- **Dynamic Model Mapping**: Automatically map Python classes to database tables with field validation and relational support.
- **Advanced Query Builder**: Intuitive querying with dynamic `SELECT`, `INSERT`, `UPDATE`, and `DELETE` statements.
- **Rich Relationships**: Support for `One-to-One`, `One-to-Many`, `Many-to-Many`, and polymorphic `Morph` relationships.
- **Migrations Manager**: Create, apply, and rollback migrations seamlessly.
- **Asynchronous & Synchronous Database Operations**: Flexible execution modes to match your application’s needs.
- **Caching Mechanisms**: Built-in query caching for optimized performance.
- **Debugging & Logging**: Configurable debug and logging options for streamlined troubleshooting.
- **Open for Personal & Commercial Use**: Use Hermes ORM freely in personal and commercial projects (not for resale as a standalone product).

---

## 🛠️ Getting Started

### Step 1: Install Hermes ORM

Install Hermes ORM via pip:

```bash
pip install hermes-orm
```

### Step 2: Define Your Models

Define models that represent your database structure:

```python
from hermes.model import BaseModel
from hermes.fields import IntegerField, StringField, ForeignKeyField

class User(BaseModel):
    id = IntegerField(primary_key=True)
    name = StringField(max_length=255, nullable=False)

class Post(BaseModel):
    id = IntegerField(primary_key=True)
    user_id = ForeignKeyField("User", nullable=False)
    content = StringField(nullable=False)
```

### Step 3: Run Migrations

Use the CLI to generate and apply migrations:

```bash
hermes make_migration create_users_table create
hermes migrate
```

### Step 4: Query the Database

Perform operations on your models:

```python
# Create a user
user = User(name="Alice")
user.save(db_connection)

# Fetch all posts
posts = Post.all(db_connection)

# Add a post for a user
post = Post(user_id=user.id, content="Hello, Hermes!")
post.save(db_connection)
```

---

## 🧩 Supported Relationships

- **One-to-One**: Easily map one-to-one relationships with `OneToOne` fields.
- **One-to-Many**: Establish hierarchical relationships with `OneToMany`.
- **Many-to-Many**: Simplify complex mappings with `ManyToMany` pivot tables.
- **Polymorphic**: Use `MorphOne` and `MorphMany` for flexible, type-based relations.

Each relationship is implemented with robust utilities for querying and manipulation.

---

## 📦 Latest Version

- **Version**: 0.1.2  
- **Release Date**: November 28, 2024

---

## 🔍 Project Status

![Closed Issues](https://img.shields.io/github/issues-closed/altxriainc/hermes)
![Enhancement Issues](https://img.shields.io/github/issues/altxriainc/hermes/enhancement)
![Bug Issues](https://img.shields.io/github/issues/altxriainc/hermes/bug)

Hermes ORM is under active development, with new features and improvements added regularly. Contributions and feedback are welcome!

---

## 📜 License and Usage

Hermes ORM is free to use for both personal and commercial projects. However, Hermes ORM itself cannot be resold or distributed as a standalone product.

---

## 🤝 Contributors

Developed and maintained by **Altxria Inc.** with contributions from a growing community of developers.

![Contributors](https://contrib.rocks/image?repo=altxriainc/hermes)

[See All Contributors](https://github.com/altxriainc/hermes/graphs/contributors)

---

## ❤️ Support Hermes ORM

If you find Hermes ORM useful, consider supporting its development and ongoing maintenance:

[![Sponsor Hermes ORM](https://img.shields.io/badge/Sponsor-Hermes%20ORM-blue?logo=github-sponsors)](https://github.com/sponsors/altxriainc)
