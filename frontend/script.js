document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const resultSection = document.getElementById('result-section');
    const previewImage = document.getElementById('preview-image');
    const nicheResult = document.getElementById('niche-result');
    const confidenceResult = document.getElementById('confidence-result');
    const keywordsList = document.getElementById('keywords-list');
    const btnCorrect = document.getElementById('btn-correct');
    const btnIncorrect = document.getElementById('btn-incorrect');
    const correctionForm = document.getElementById('correction-form');
    const nicheSelect = document.getElementById('niche-select');
    const btnSubmitCorrection = document.getElementById('btn-submit-correction');

    let currentHistoryId = null;

    // Load niches for dropdown
    fetch('/niches')
        .then(res => res.json())
        .then(niches => {
            niches.forEach(niche => {
                const option = document.createElement('option');
                option.value = niche.id;
                option.textContent = niche.name;
                nicheSelect.appendChild(option);
            });
        });

    // Upload handling
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = '#ccc';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.backgroundColor = '';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = '';
        if (e.dataTransfer.files.length) {
            handleUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleUpload(fileInput.files[0]);
        }
    });

    function handleUpload(file) {
        const formData = new FormData();
        formData.append('file', file);

        // Show preview immediately
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            resultSection.classList.remove('hidden');
            nicheResult.textContent = "ANALYZING...";
            confidenceResult.textContent = "---";
            keywordsList.innerHTML = "";
            correctionForm.classList.add('hidden');
        };
        reader.readAsDataURL(file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                currentHistoryId = data.history_id;
                nicheResult.textContent = data.classification.niche;
                confidenceResult.textContent = data.classification.confidence;

                keywordsList.innerHTML = '';
                data.labels.forEach(label => {
                    const li = document.createElement('li');
                    li.textContent = label;
                    keywordsList.appendChild(li);
                });
            })
            .catch(err => {
                console.error(err);
                nicheResult.textContent = "ERROR";
            });
    }

    // Feedback handling
    btnCorrect.addEventListener('click', () => {
        if (!currentHistoryId) return;
        submitFeedback('correct');
        alert('FEEDBACK RECORDED. THANKS.');
    });

    btnIncorrect.addEventListener('click', () => {
        correctionForm.classList.remove('hidden');
    });

    btnSubmitCorrection.addEventListener('click', () => {
        if (!currentHistoryId) return;
        const selectedNiche = nicheSelect.value;
        if (!selectedNiche) {
            alert('SELECT A NICHE');
            return;
        }
        submitFeedback('incorrect', selectedNiche);
        alert('CORRECTION RECORDED. THANKS.');
        correctionForm.classList.add('hidden');
    });

    function submitFeedback(type, nicheId = null) {
        fetch('/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                history_id: currentHistoryId,
                feedback: type,
                corrected_niche_id: nicheId
            })
        });
    }
});
