import subprocess
import sys
import json

def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e.stderr)
        sys.exit(1)

def parse_classrooms(output):
    """Parse the output of gh classroom list to get list of (id, name)."""
    lines = output.split('\n')
    classrooms = []
    if len(lines) < 3:
        return classrooms
    for line in lines[2:]:  # Skip "X Classrooms" and header
        if line.strip():
            parts = line.split()
            if len(parts) >= 3:
                classroom_id = parts[0].strip()
                url = parts[-1].strip()
                name = ' '.join(parts[1:-1]).strip()
                classrooms.append((classroom_id, name))
    return classrooms

def parse_assignments(output):
    """Parse the output of gh classroom assignments to get list of (id, title)."""
    lines = output.split('\n')
    assignments = []
    if len(lines) < 3:
        return assignments
    for line in lines[2:]:  # Skip "X Assignments" and header
        if line.strip():
            parts = line.split()
            if len(parts) >= 3:
                assignment_id = parts[0].strip()
                url = parts[-1].strip()
                title = ' '.join(parts[1:-1]).strip()
                assignments.append((assignment_id, title))
    return assignments

def parse_accepted_assignments(output):
    """Parse the output of gh classroom accepted-assignments to get list of (user, url)."""
    lines = output.split('\n')[4:]  # Skip header lines
    accepted = []
    for line in lines:
        if line.strip():
            parts = line.split('\t')
            if len(parts) >= 2:
                user = parts[-2].strip()
                url = parts[-1].strip()
                accepted.append((user, url))
    return accepted

def has_pending_invitation(org, repo, user):
    """Check if user has a pending invitation to the repo and return the invitation ID if found."""
    command = f'gh api /repos/{org}/{repo}/invitations'
    try:
        output = run_command(command)
        invitations = json.loads(output)
        for inv in invitations:
            if inv.get('invitee', {}).get('login') == user:
                return inv.get('id')
        return None
    except json.JSONDecodeError:
        return None
    except subprocess.CalledProcessError:
        return None

def delete_invitation(org, repo, invitation_id):
    """Delete a pending invitation by ID."""
    command = f'gh api -X DELETE /repos/{org}/{repo}/invitations/{invitation_id} --silent'
    print(f"Deleting pending invitation for {org}/{repo} (ID: {invitation_id})")
    run_command(command)

def add_collaborator(org, repo, user):
    """Add user as collaborator to the repo."""
    command = f'gh api -X PUT /repos/{org}/{repo}/collaborators/{user} -f permission=write --silent'
    print(f"Adding {user} to {org}/{repo}")
    run_command(command)

def main():
    # List classrooms
    print("Fetching classrooms...")
    output = run_command('gh classroom list')
    classrooms = parse_classrooms(output)
    if not classrooms:
        print("No classrooms found.")
        return

    print("Available classrooms:")
    for i, (cid, name) in enumerate(classrooms, 1):
        print(f"{i}. {name} (ID: {cid})")

    # Select classroom
    while True:
        try:
            choice = int(input("Select a classroom (number): ")) - 1
            if 0 <= choice < len(classrooms):
                selected_classroom = classrooms[choice]
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")

    classroom_id, classroom_name = selected_classroom
    print(f"Selected: {classroom_name}")

    # List assignments for the classroom
    print(f"Fetching assignments for classroom {classroom_name}...")
    output = run_command(f'gh classroom assignments -c {classroom_id}')
    assignments = parse_assignments(output)
    if not assignments:
        print("No assignments found.")
        return

    print("Available assignments:")
    for i, (aid, title) in enumerate(assignments, 1):
        print(f"{i}. {title} (ID: {aid})")

    # Select assignment
    while True:
        try:
            choice = int(input("Select an assignment (number): ")) - 1
            if 0 <= choice < len(assignments):
                selected_assignment = assignments[choice]
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a number.")

    assignment_id, assignment_title = selected_assignment
    print(f"Selected: {assignment_title}")

    # Fetch and fix accepted assignments
    page = 1
    while True:
        print(f"Fetching page {page} of accepted assignments...")
        command = f'gh classroom accepted-assignments -a {assignment_id} --per-page 30 --page {page}'
        output = run_command(command)
        accepted = parse_accepted_assignments(output)
        if not accepted:
            break
        for user, url in accepted:
            url_parts = url.split('/')
            if len(url_parts) >= 2:
                org = url_parts[-2]
                repo = url_parts[-1]
                invitation_id = has_pending_invitation(org, repo, user)
                if invitation_id:
                    delete_invitation(org, repo, invitation_id)
                    add_collaborator(org, repo, user)
                else:
                    print(f"Skipping {user} for {org}/{repo} (no pending invitation)")
        page += 1

    print("Done fixing pending invitations.")

if __name__ == "__main__":
    main()

