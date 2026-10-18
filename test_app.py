
import app as employee_app
import sqlite3
import tempfile
import unittest
import os


class EmployeeAPITest(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()

        self.original_database = employee_app.DATABASE
        employee_app.DATABASE = self.temp_db.name

        connection = sqlite3.connect(employee_app.DATABASE)
        connection.execute("""
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                empid TEXT NOT NULL UNIQUE,
                dob TEXT NOT NULL,
                state TEXT NOT NULL
            )
        """)
        connection.commit()
        connection.close()

        self.client = employee_app.app.test_client()

    def tearDown(self):
        employee_app.DATABASE = self.original_database
        os.unlink(self.temp_db.name)

    def test_get_employees(self):
        response = self.client.get('/api/employees')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_register_employee(self):
        response = self.client.post(
            '/api/employees',
            json={
                'name': 'Test Employee',
                'empid': 'TEST1001',
                'dob': '1995-05-10',
                'state': 'Kerala'
            }
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.get_json()['message'],
            'Employee registered successfully'
        )

    def test_missing_fields(self):
        response = self.client.post(
            '/api/employees',
            json={'name': 'Test Employee'}
        )

        self.assertEqual(response.status_code, 400)

    def test_duplicate_employee_id(self):
        employee = {
            'name': 'Test Employee',
            'empid': 'TEST1001',
            'dob': '1995-05-10',
            'state': 'Kerala'
        }

        self.client.post('/api/employees', json=employee)
        response = self.client.post('/api/employees', json=employee)

        self.assertEqual(response.status_code, 409)


if __name__ == '__main__':
    unittest.main(verbosity=2)

