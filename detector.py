from colorama import Fore, Style, init
import instaloader
import csv
import re
from datetime import datetime

init(autoreset=True)

BANNER = f"""{Fore.CYAN}
==========================================
          FAKE ID DETECTION TOOL
==========================================
{Style.RESET_ALL}
"""



class InstagramAudit:
    def _init_(self):   

        self.L = instaloader.Instaloader()
        self.L.request_timeout = 30

    def scrape_profile(self, username):
        """Scrape public profile data."""
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
            return {
                'username': profile.username,
                'followers': profile.followers,
                'following': profile.followees,
                'total_posts': profile.mediacount,
                'is_private': profile.is_private,
                'scraped_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"{Fore.RED}⚠️ Error scraping @{username}: {str(e)}")
            return None

    def manual_input(self):
        """Collect manual input for missing data."""
        print(f"\n{Fore.YELLOW}📝 Manual Data Entry")
        return {
            'account_age_days': int(input(f"{Fore.WHITE}Account age (days): ")),
            'avg_likes': float(input(f"{Fore.WHITE}Average likes per post: ")),
            'avg_comments': float(input(f"{Fore.WHITE}Average comments per post: ")),
            'stolen_content': input(f"{Fore.WHITE}Stolen content? (y/n): ").lower() == 'y'
        }

    def analyze_account(self, data):
        """Detect fake accounts with scoring."""
        score = 0
        reasons = []

        # Username Analysis
        if re.search(r'\d{4,}', data['username']):
            score += 1
            reasons.append("Suspicious username")
        
        # Follower-Following Ratio
        if data['followers'] < 100 and data['following'] > 1500:
            score += 3
            reasons.append("Extreme follower-following ratio")

        # Engagement Analysis
        engagement = (data['avg_likes'] + data['avg_comments']) / max(data['followers'], 1) * 100
        if engagement < 1:
            score += 2
            reasons.append("Low engagement (<1%)")

        # Account Age vs. Posts
        if data['total_posts'] == 0 and data['account_age_days'] > 7:
            score += 2
            reasons.append("No posts despite old account")

        # Stolen Content
        if data.get('stolen_content'):
            score += 3
            reasons.append("Stolen content detected")

        confidence = min(score * 10, 100)
        return {
            'is_fake': score >= 5,
            'confidence': confidence,
            'reasons': reasons,
            'risk_score': score
        }

    def process_csv(self, input_file, output_file):
        """Bulk analyze accounts from CSV."""
        with open(input_file, mode='r') as file:
            reader = csv.DictReader(file)
            accounts = [row for row in reader if 'username' in row]

        results = []
        for account in accounts:
            username = account['username']
            print(f"\n{Fore.CYAN}Analyzing @{username}...")

            # Scrape or use manual data
            scraped_data = self.scrape_profile(username) or {}
            manual_data = {
                'account_age_days': int(account.get('account_age_days', 365)),
                'avg_likes': float(account.get('avg_likes', 0)),
                'avg_comments': float(account.get('avg_comments', 0)),
                'stolen_content': account.get('stolen_content', '').lower() == 'y'
            }
            combined_data = {**scraped_data, **manual_data}

            # Analyze and save
            analysis = self.analyze_account(combined_data)
            result = {**combined_data, **analysis}
            results.append(result)

            # Print result
            verdict = f"{Fore.RED}FAKE" if result['is_fake'] else f"{Fore.GREEN}REAL"
            print(f"{Fore.WHITE}Verdict: {verdict}{Style.RESET_ALL} | Confidence: {result['confidence']}%")

        # Save to CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"\n{Fore.GREEN}✅ Results saved to {output_file}")

    def single_account_mode(self):
        """Analyze a single account interactively."""
        username = input(f"\n{Fore.WHITE}Enter Instagram username: ").strip()
        scraped_data = self.scrape_profile(username) or {'username': username}
        manual_data = self.manual_input()
        combined_data = {**scraped_data, **manual_data}

        analysis = self.analyze_account(combined_data)
        print(f"\n{Fore.CYAN}=== ANALYSIS REPORT ===")
        print(f"{Fore.WHITE}👤 @{combined_data['username']}")
        print(f"{Fore.WHITE}🔢 Followers: {combined_data['followers']} | Following: {combined_data['following']}")
        print(f"{Fore.WHITE}📊 Risk Score: {analysis['risk_score']}/10 | Confidence: {analysis['confidence']}%")

        if analysis['is_fake']:
            print(f"{Fore.RED}🚨 VERDICT: Likely Fake Account")
        else:
            print(f"{Fore.GREEN}✅ VERDICT: Genuine Account")

        if analysis['reasons']:
            print(f"\n{Fore.YELLOW}🚩 Red Flags: {', '.join(analysis['reasons'])}")

def main():
    print(BANNER)
    print(f"{Fore.YELLOW} Instagram Fake Account Detector")
    audit = InstagramAudit()

    while True:
        print(f"\n{Fore.CYAN}=== MENU ===")
        print(f"{Fore.WHITE}1. Analyze a single account")
        print(f"{Fore.WHITE}2. Bulk analyze from CSV")
        print(f"{Fore.WHITE}3. Exit")
        choice = input(f"{Fore.YELLOW}Choose an option (1-3): ")

        if choice == '1':
            audit.single_account_mode()
        elif choice == '2':
            input_file = input(f"{Fore.WHITE}Enter CSV filename (e.g., accounts.csv): ")
            output_file = input(f"{Fore.WHITE}Save results to (e.g., results.csv): ")
            audit.process_csv(input_file, output_file)
        elif choice == '3':
            print(f"{Fore.MAGENTA}👋 Goodbye!")
            break
        else:
            print(f"{Fore.RED}Invalid choice!")

if __name__ == "__main__":

    main()