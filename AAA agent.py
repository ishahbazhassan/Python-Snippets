def score_lead(lead):
    score = 0
    if lead['industry'] in ['Finance', 'Tech']:
        score += 30
    if lead['budget'] > 10000:
        score += 40
    if lead['location'] == 'USA':
        score += 30
    return score

def assign_agent(lead_score):
    if lead_score > 80:
        return 'Senior Agent'
    elif lead_score > 50:
        return 'Intermediate Agent'
    else:
        return 'Junior Agent'

# Example usage
lead = {'industry': 'Tech', 'budget': 15000, 'location': 'USA'}
score = score_lead(lead)
agent = assign_agent(score)
print(f"Lead Score: {score}, Assigned Agent: {agent}")
