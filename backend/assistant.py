import pyttsx3  # bibliothèque pour la synthèse vocale
import pandas as pd  # bibliothèque pour la manipulation de données
import speech_recognition as sr  # bibliothèque pour la reconnaissance vocale
import os  # bibliothèque pour les opérations liées au système d'exploitation

# Initialisation du moteur de synthèse vocale
engine = pyttsx3.init()

# Configuration de la vitesse de parole
engine.setProperty('rate', 150)


# Fonction pour lire les données sur les ordinateurs portables depuis un fichier CSV
def read_laptop_data(file_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, file_name)
    laptops_df = pd.read_csv(file_path, delimiter=',')
    laptops_df.columns = laptops_df.columns.str.strip()  # Suppression des espaces superflus dans les noms de colonnes
    return laptops_df

# Fonction pour filtrer les ordinateurs portables en fonction des critères de l'utilisateur
def filter_laptops(laptops_df, criteria):
    filtered_laptops_df = laptops_df.copy()  # Copie du DataFrame original
    valid_keys = laptops_df.columns.tolist()  # Liste des colonnes valides

    # Vérification des critères fournis par l'utilisateur
    for key, value in criteria.items():
        if key not in valid_keys:
            print(f"Error: '{key}' is not a valid key in the laptop data. Valid keys are: {valid_keys}")
            return None

    # Filtrage des ordinateurs portables en fonction de la marque spécifiée
    if 'Company' in criteria and 'Company' in filtered_laptops_df.columns:
        filtered_laptops_df = filtered_laptops_df[filtered_laptops_df['Company'].str.lower() == criteria['Company'].lower()]
    else:
        print("Error: 'Company' column does not exist in the laptop data or brand criteria not specified.")
        return None

    # Filtrage des ordinateurs portables en fonction du prix spécifié
    if 'Price' in criteria and 'Price' in filtered_laptops_df.columns:
        try:
            filtered_laptops_df['Price'] = pd.to_numeric(filtered_laptops_df['Price'], errors='coerce')
        except KeyError:
            print("Error: 'Price' column does not exist in the laptop data.")
            return None
        filtered_laptops_df = filtered_laptops_df[filtered_laptops_df['Price'] <= criteria['Price']]
    else:
        print("Error: 'Price' column does not exist in the laptop data or price criteria not specified.")
        return None
    
    return filtered_laptops_df

# Fonction pour reconnaître la parole
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio)
        print("You said:", query)
        return query
    except sr.UnknownValueError:
        print("Sorry, I couldn't understand. Please try again.")
        return None
    except sr.RequestError as e:
        print("Error occurred; {0}".format(e))
        return None

# Fonction pour parler la réponse
def speak_response(response):
    print("Assistant says:", response)
    engine.say(response)
    engine.runAndWait()

# Fonction principale pour l'interaction utilisateur
def main():
    # Lecture des données sur les ordinateurs portables depuis un fichier CSV
    laptops_df = read_laptop_data('Laptop_data.csv')

    # Initialisation des critères de recherche
    criteria = {'Company': None, 'Price': None}

    # Demande à l'utilisateur la marque recherchée
    speak_response("What brand are you looking for?")
    brand = recognize_speech()
    if brand:
        criteria['Company'] = brand
    else:
        speak_response("Sorry, I couldn't understand. Let's try again.")
        return

    # Demande à l'utilisateur le budget maximum
    speak_response("What is your maximum budget (in euros)?")
    price = recognize_speech()
    if price:
        # Conversion du prix en valeur numérique
        numeric_price = ''.join(filter(str.isdigit, price))
        try:
            criteria['Price'] = float(numeric_price)
        except ValueError:
            speak_response("Sorry, I couldn't understand the price. Please try again.")
            return
    else:
        speak_response("Sorry, I couldn't understand. Let's try again.")
        return

    print("Criteria:", criteria)  # Affichage des critères de recherche (pour le débogage)

    # Filtrage des ordinateurs portables en fonction des critères de recherche
    filtered_laptops_df = filter_laptops(laptops_df, criteria)

    # Affichage des résultats de la recherche
    if filtered_laptops_df is not None and not filtered_laptops_df.empty:
        speak_response("Here are some laptops that match your criteria:")
        for index, laptop in filtered_laptops_df.iterrows():
            speak_response(f"{laptop['Product']} - {laptop['Price']} euros")

        # Demande à l'utilisateur de choisir un ordinateur portable
        speak_response("Please choose a laptop by saying its position in the list.")
        choice = recognize_speech()
        if choice:
            # Convertir le choix de l'utilisateur en un index de liste
            if any(word in choice.lower() for word in ['first', '1st']):
                index = 0
            elif any(word in choice.lower() for word in ['second', '2nd']):
                index = 1
            elif any(word in choice.lower() for word in ['third', '3rd']):
                index = 2
            elif any(word in choice.lower() for word in ['fourth', '4th']):
                index = 3
            elif any(word in choice.lower() for word in ['fifth', '5th']):
                index = 4
            else:
                speak_response("Sorry, I couldn't understand your choice. Please try again.")
                return

            # Vérifier si l'index est valide et choisir l'ordinateur portable correspondant
            if 0 <= index < len(filtered_laptops_df):
                chosen_laptop = filtered_laptops_df.iloc[index]
                speak_response(f"Your laptop {chosen_laptop['Product']} is added to your bag. Please check it and complete the payment process.")
            else:
                speak_response("Sorry, I couldn't understand your choice. Please try again.")
    else:
        speak_response("Sorry, no laptops matching your criteria were found.")

# Exécution de la fonction principale si le script est exécuté directement
if __name__ == "__main__":
    main()


# Exécution de la fonction principale si le script est exécuté directement
if __name__ == "__main__":
    main()
