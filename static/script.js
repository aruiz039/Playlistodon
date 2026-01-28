document.getElementById('playlistForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const playlistName = document.getElementById('playlistName').value.trim();
    const hashtag = document.getElementById('hashtag').value.trim();

    if (!playlistName || !hashtag) {
        alert('Please fill in all fields');
        return;
    }

    // Show loading state
    document.getElementById('playlistForm').classList.add('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');

    // Disable button
    const submitBtn = document.querySelector('.btn-submit');
    submitBtn.disabled = true;

    try {
        const response = await fetch('/create_playlist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                playlistName: playlistName,
                hashtag: hashtag
            })
        });

        const data = await response.json();

        if (data.success) {
            // Show result
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('resultPlaylistName').textContent = data.playlistName;
            document.getElementById('resultAdded').textContent = data.addedCount;
            document.getElementById('resultSkipped').textContent = data.skippedCount;
            
            const playlistLink = document.getElementById('playlistLink');
            playlistLink.href = data.playlistUrl;
            
            document.getElementById('result').classList.remove('hidden');
        } else {
            throw new Error(data.error || 'An error occurred');
        }
    } catch (error) {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('errorMessage').textContent = error.message;
        document.getElementById('error').classList.remove('hidden');
    } finally {
        submitBtn.disabled = false;
    }
});

function resetForm() {
    document.getElementById('playlistForm').reset();
    document.getElementById('result').classList.add('hidden');
    document.getElementById('playlistForm').classList.remove('hidden');
}

function closeError() {
    document.getElementById('error').classList.add('hidden');
    document.getElementById('playlistForm').classList.remove('hidden');
}
