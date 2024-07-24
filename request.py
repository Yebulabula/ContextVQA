import os
import git

def commit_and_push(repo, files, batch_number):
    repo.index.add(files)
    repo.index.commit(f'Batch upload {batch_number}')
    origin = repo.remote(name='origin')
    origin.push()

def upload_files_in_batches(directory, batch_size):
    # repo = git.Repo(directory)
    repo = git.Repo('')  # Replace with your local repository path
    files = [os.path.join(directory, f) for f in os.listdir(directory)]
    total_files = len(files)
    print(f'Total files: {total_files}')
    for i in range(0, total_files, batch_size):
        batch = files[i:i + batch_size]
        commit_and_push(repo, batch, i//batch_size + 1)
        print(f'Batch {i//batch_size + 1} of {total_files//batch_size + 1} complete.')

directory = '3D_scans'  # Replace with your local repository path
batch_size = 10
upload_files_in_batches(directory, batch_size)
