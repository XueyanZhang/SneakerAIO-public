#!/usr/bin/env python3

import os
import json
from pathlib import Path
from dataclasses import dataclass, astuple, asdict

@dataclass
class Profile:
    email: str
    password: str
    size: str
    cvv: str
    login_url: str
    product_url: str
    release_time: str
    driver_type: str

    def __init__(self, profile_book: dict):
        self.email = profile_book["email"]
        self.password = profile_book["password"]
        self.size = profile_book["size"]
        self.cvv = profile_book["cvv"]
        self.login_url = profile_book["login_url"]
        self.product_url = profile_book["product_url"]
        self.release_time = profile_book["release_time"]
        self.driver_type = profile_book["driver_type"]


class ProfileManager():
    def load_profile(self, profile_name: str) -> Profile:
        profile = self.locate_profile(profile_name)
        with profile.open() as f:
            profile_book = json.load(f)
        return Profile(profile_book)

    def locate_profile(self, profile_name: str) -> Path:
        profile_folder = Path("./profile/")
        for profile in profile_folder.iterdir():
            if f"{profile_name}.json" in profile.name:
                return profile
        raise Exception('Profile not found')

    def add_profile(self):
        # ...
        self.validate_profile()
        pass

    def validate_profile(self):
        pass