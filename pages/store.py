def determine_asset_filename(reward_key, index_fallback):
    """
    Constructs accurate GitHub direct raw paths from the numeric Reward Keys.
    Forces case-matched extensions to prevent server 404 errors.
    """
    # Pull any integers out of your key column (e.g., '1' -> '1')
    digits = re.findall(r'\d+', str(reward_key))
    num_id = digits[0] if digits else str(index_fallback + 1)
    
    github_user = "joyb02-repo"
    github_repo = "MedallionManager"
    
    # Using 'main' as verified from your navigation bar and forcing the '.jpg' extension casing
    return f"https://raw.githubusercontent.com/{github_user}/{github_repo}/main/assets/Reward{num_id}.jpg"
