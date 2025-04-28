document.addEventListener('DOMContentLoaded', function() {
    // File upload preview and validation
    const fileInput = document.getElementById('cv_file');
    const fileLabel = document.querySelector('.custom-file-label');
    const submitBtn = document.getElementById('submit-btn');
    const uploadForm = document.getElementById('upload-form');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                const fileName = fileInput.files[0].name;
                fileLabel.textContent = fileName;
                
                // Check file extension
                const fileExt = fileName.split('.').pop().toLowerCase();
                if (['pdf', 'docx'].indexOf(fileExt) === -1) {
                    showAlert('Please upload a PDF or DOCX file only', 'danger');
                    submitBtn.disabled = true;
                } else {
                    submitBtn.disabled = false;
                }
                
                // Check file size
                const fileSize = fileInput.files[0].size;
                const maxSize = 16 * 1024 * 1024; // 16MB
                if (fileSize > maxSize) {
                    showAlert('File is too large. Maximum size is 16MB', 'danger');
                    submitBtn.disabled = true;
                }
            } else {
                fileLabel.textContent = 'Choose file';
                submitBtn.disabled = true;
            }
        });
    }
    
    // Show loading indicator on form submit
    if (uploadForm) {
        uploadForm.addEventListener('submit', function() {
            if (loadingIndicator) {
                loadingIndicator.classList.remove('d-none');
            }
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
        });
    }
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Function to create and show alerts
    function showAlert(message, type) {
        const alertContainer = document.getElementById('alert-container');
        if (!alertContainer) return;
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.role = 'alert';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alertContainer.removeChild(alert);
            }, 150);
        }, 5000);
    }
    
    // Collapsible job descriptions
    const jobDescriptionToggles = document.querySelectorAll('.job-description-toggle');
    if (jobDescriptionToggles.length > 0) {
        jobDescriptionToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const jobId = this.getAttribute('data-job-id');
                const descriptionElement = document.getElementById(`job-description-${jobId}`);
                
                if (descriptionElement.classList.contains('d-none')) {
                    descriptionElement.classList.remove('d-none');
                    this.innerHTML = '<i class="bi bi-chevron-up"></i> Hide Description';
                } else {
                    descriptionElement.classList.add('d-none');
                    this.innerHTML = '<i class="bi bi-chevron-down"></i> Show Description';
                }
            });
        });
    }
    
    // Match score visualization
    const matchScoreElements = document.querySelectorAll('.match-score');
    if (matchScoreElements.length > 0) {
        matchScoreElements.forEach(element => {
            const score = parseFloat(element.getAttribute('data-score'));
            let colorClass = 'bg-danger';
            
            if (score >= 80) {
                colorClass = 'bg-success';
            } else if (score >= 60) {
                colorClass = 'bg-info';
            } else if (score >= 40) {
                colorClass = 'bg-warning';
            }
            
            element.querySelector('.progress-bar').className = `progress-bar ${colorClass}`;
            element.querySelector('.progress-bar').style.width = `${score}%`;
            element.querySelector('.progress-bar').setAttribute('aria-valuenow', score);
        });
    }
});
