// Email Admin JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Add confirmation for send now button
    const sendNowButtons = document.querySelectorAll('a[href*="send_now=1"]');
    sendNowButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to send this email now? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Add status indicators
    const statusCells = document.querySelectorAll('.field-status');
    statusCells.forEach(cell => {
        const status = cell.textContent.trim().toLowerCase();
        cell.classList.add(`status-${status}`);
    });

    // Auto-refresh the page if any emails are in 'sending' state
    const sendingEmails = document.querySelectorAll('.status-sending');
    if (sendingEmails.length > 0) {
        setTimeout(() => {
            window.location.reload();
        }, 5000); // Reload every 5 seconds while sending
    }

    // Add tooltips for error messages
    const errorLogs = document.querySelectorAll('.field-last_error');
    errorLogs.forEach(log => {
        if (log.textContent.trim()) {
            log.setAttribute('title', log.textContent);
            log.style.cursor = 'help';
            log.style.borderBottom = '1px dashed #999';
        }
    });
});
