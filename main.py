from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from modules.stt_handler import transcribe_audio
from modules.tts_handler import speak
from datetime import datetime
from modules.intent_logic import match_intent

class HomeScreen(Screen):
    pass

class ContactScreen(Screen):
    pass

class MapScreen(Screen):
    pass

# --- App ---
class GrabBuddyApp(App):
    current_phase = StringProperty("Idle")       # "Idle" or "Pickup"
    listening = BooleanProperty(False)           # Controls bottom footer
    current_response = StringProperty("")        # Optional: bind to label later
    listening_text = StringProperty("Call 'Hey Buddy' for help...")

    def build(self):
        Builder.load_file("screen_layout.kv")
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ContactScreen(name="contact"))
        sm.add_widget(MapScreen(name="map"))
        return sm

    def on_start(self):
        self.update_guidance()

    # Handle phase switching (via Spinner or simulated input)
    def set_trip_phase(self, new_phase):
        self.current_phase = new_phase
        self.update_guidance()

    def update_guidance(self):
        """Update the guidance_label and trip phase indicator"""
        guidance_text = {
            "Idle": (
                "Now your trip phase is: Idle.\n"
                "You may ask:\n"
                "1) Your Performance\n"
                "2) New Order\n"
                "3) Total Income of the day\n"
                "4) Total Hours\n"
                "5) Take a Short Break"
            ),
            "Pickup": (
                "Trip phase: Pickup.\n"
                "You may ask:\n"
                "1) Reconfirm Trip\n"
                "2) ETA to Pickup\n"
                "3) Passenger Info\n"
                "4) Time Check\n"
                "5) Back to Map\n"
                "6) Cancel Trip"
            )
        }

        phase_color = "[color=00ff00]●[/color]" if self.current_phase == "Idle" else "[color=ffff00]●[/color]"
        home_screen = self.root.get_screen("home")

        # Update guidance
        home_screen.ids.guidance_label.text = guidance_text[self.current_phase]

        # Update dot + label
        home_screen.ids.phase_indicator.text = f"{phase_color} TRIP PHASE: {self.current_phase.upper()}"

    def handle_button(self, action):
        """Handle what happens when buttons are pressed"""
        print(f"[Button] {action}")
        self.listening = False

        if action == "reconfirm":
            self.respond("You are picking up the passenger at 41A, Jalan Keria.")
        elif action == "eta":
            self.respond("Your ETA to pickup is 7:37 PM.")
        elif action == "time":
            from datetime import datetime
            now = datetime.now().strftime("%I:%M %p")
            self.respond(f"The current time is {now}.")
        elif action == "cancel":
            self.respond("Okay, the trip has been cancelled.")
        elif action == "map":
            self.change_screen("map")
        else:
            Clock.schedule_once(lambda dt: self.respond(action), 1.2)

    def send_message(self):
        screen = self.root.get_screen("contact")
        msg = screen.ids.message_input.text.strip()
        if msg:
            self.add_message_to_chat(msg, sender="driver")
            screen.ids.message_input.text = ""

    def clear_message(self):
        screen = self.root.get_screen("contact")
        screen.ids.message_input.text = ""

    def add_message_to_chat(self, message, sender="driver"):
        from kivy.uix.label import Label
        screen = self.root.get_screen("contact")
        chat = screen.ids.message_box

        # Different bubble color based on sender
        if sender == "driver":
            color = [1, 1, 1, 1]  # white
        else:
            color = [0.85, 0.85, 0.85, 1]  # light gray

        bubble = Label(
            text=message,
            size_hint_y=None,
            height=30,
            halign="left" if sender == "driver" else "right",
            valign="middle",
            text_size=(self.root.width - 40, None),
            padding=(10, 10),
            color=(0, 0, 0, 1)
        )

        bubble.canvas.before.clear()
        with bubble.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*color)
            Rectangle(pos=bubble.pos, size=bubble.size)

        chat.add_widget(bubble)

    def respond(self, action):
        """Return assistant response based on action and phase"""
        # Responses based on phase
        idle_responses = {
            "performance": "You’ve completed 4 trips so far today and earned RM82. Great job!",
            "new_order": "You have a new order from Jalan Bunga Raya!",
            "income": "Your total income today is RM82.50.",
            "hours": "You’ve been active for 2 hours and 20 minutes.",
            "short_break": "Alright. Starting a short break — I’ll remind you in 10 minutes."
        }

        pickup_responses = {
            "reconfirm": "Your destination is Sunway Pyramid. Fare is RM14.",
            "eta": "You're 4 minutes away from your passenger.",
            "contact": "Opening contact screen...",
            "time": "Pickup is scheduled for 3:45 PM.",
            "map": "Opening map view.",
            "cancel": "Trip cancelled. Returning to idle."
        }

        response = ""
        action = action.lower()
        phase = self.current_phase.lower()

        if phase == "idle":
            response = idle_responses.get(action, "I'm still learning to assist with that.")
        elif phase == "pickup":
            response = pickup_responses.get(action, "Let me check on that for you.")

        speak(response)
        
        # Update response label
        home_screen = self.root.get_screen("home")
        if "response_label" in home_screen.ids:
            home_screen.ids.response_label.text = response

        # Navigate if needed
        if action == "map":
            self.change_screen("map")
        elif action == "contact":
            self.change_screen("contact")
        elif action == "cancel":
            self.set_trip_phase("Idle")

        self.listening = False

    def change_screen(self, screen_name):
        self.root.current = screen_name
    
    def start_listening(self):
        self.listening = True
        self.listening_text = "Listening..."
        Clock.schedule_once(lambda dt: self.process_voice_input(), 0.5)

    def process_voice_input(self):
        text = transcribe_audio()
        
        self.listening = False
        self.listening_text = "Call 'Hey Buddy' for help..."

        self.handle_transcribed_input(text)


    def handle_transcribed_input(self, text):
        print(f"[Input] You said: {text}")
        intent = match_intent(text)

        if "buddy send" in text.lower():
            self.send_message()
            return
        elif "buddy clear" in text.lower():
            self.clear_message()
            return

        if intent:
            self.handle_button(intent)
        else:
            self.root.get_screen("home").ids.response_label.text = "Sorry, I didn’t understand that."

if __name__ == "__main__":
    GrabBuddyApp().run()