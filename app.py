from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import logging

app = Flask(__name__)

# Set up logging for easier debugging in production
logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    conn = sqlite3.connect('contacts.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'name' in request.form and 'phone' in request.form:
            name = request.form['name']
            phone_number = request.form['phone']
            email = request.form.get('email', '')  # Get email
            birthday = request.form.get('birthday', '')  # Get birthday

            conn = get_db_connection()
            conn.execute('INSERT INTO contacts (name, phone_number, email, birthday) VALUES (?, ?, ?, ?)', 
                         (name, phone_number, email, birthday))
            conn.commit()
            conn.close()

            return redirect(url_for('index'))
        else:
            return 'Error: Name and phone number are required.', 400

    conn = get_db_connection()
    contacts = conn.execute('SELECT * FROM contacts').fetchall()
    conn.close()

    return render_template('index.html', contacts=contacts)

@app.route('/delete/<int:id>', methods=['GET'])
def delete_contact(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM contacts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_contact(id):
    try:
        # Récupérer les données du formulaire
        name = request.form.get("name")
        phone_number = request.form.get("phone")
        email = request.form.get("email")
        birthday = request.form.get("birthday")

        # Vérifier si les données sont présentes
        if not name or not phone_number:
            return jsonify({"success": False, "message": "Le nom et le numéro de téléphone sont requis."}), 400

        # Connexion à la base de données
        conn = get_db_connection()

        # Exécution de la requête UPDATE
        conn.execute('UPDATE contacts SET name = ?, phone_number = ?, email = ?, birthday = ? WHERE id = ?',
                     (name, phone_number, email, birthday, id))

        # Commit des changements
        conn.commit()
        
        # Fermer la connexion
        conn.close()

        # Retourner une réponse JSON de succès
        return jsonify({"success": True, "message": "Contact mis à jour avec succès!"})

    except Exception as e:
        # Gestion des erreurs et journalisation
        logging.error(f"Erreur lors de la mise à jour du contact avec l'id {id}: {e}")
        return jsonify({"success": False, "message": str(e)}), 500



@app.route('/contact/<int:id>', methods=['GET'])
def get_contact(id):
    conn = get_db_connection()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (id,)).fetchone()
    conn.close()

    if contact:
        return jsonify(dict(contact))
    else:
        return jsonify({'error': 'Contact not found'}), 404

if __name__ == "__main__":
    app.run(debug=True)
