# Add to your existing imports
from django.contrib.auth.decorators import login_required
from .models import ComplaintComment, ComplaintLog
from django.utils import timezone

# Add this new view function
@login_required
def view_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    
    if request.method == "POST":
        comment = request.POST.get('comment')
        if comment:
            # Create new comment
            ComplaintComment.objects.create(
                complaint=complaint,
                user=request.user,
                comment=comment
            )
            
            # Log the comment action
            ComplaintLog.objects.create(
                complaint=complaint,
                user=request.user,
                action="Added comment",
                details=f"Comment added: {comment[:50]}..."
            )
            
            return redirect('view_complaint', complaint_id=complaint_id)
    
    return render(request, 'management/view_complaint.html', {
        'complaint': complaint
    })

# Modify your edit_complaint view to include logging
@login_required
def edit_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES, instance=complaint)
        if form.is_valid():
            # Get the changed fields
            changed_fields = []
            for field in form.changed_data:
                old_value = getattr(complaint, field)
                new_value = form.cleaned_data[field]
                changed_fields.append(f"{field}: {old_value} → {new_value}")
            
            # Save the complaint
            complaint = form.save()
            
            # Create log entry for the changes
            if changed_fields:
                ComplaintLog.objects.create(
                    complaint=complaint,
                    user=request.user,
                    action="Updated complaint",
                    details="Changed: " + ", ".join(changed_fields)
                )
            
            # Handle media files
            media_to_delete = request.POST.getlist('delete_media')
            for media_id in media_to_delete:
                media = ComplaintMedia.objects.get(id=media_id)
                media.file.delete()
                media.delete()
                
                ComplaintLog.objects.create(
                    complaint=complaint,
                    user=request.user,
                    action="Deleted media",
                    details=f"Deleted media file: {media.file.name}"
                )

            for file in request.FILES.getlist('media'):
                ComplaintMedia.objects.create(complaint=complaint, file=file)
                ComplaintLog.objects.create(
                    complaint=complaint,
                    user=request.user,
                    action="Added media",
                    details=f"Added new media file: {file.name}"
                )

            return redirect('complaint_list')
    else:
        form = ComplaintForm(instance=complaint)

    return render(request, 'management/edit_complaint.html', {
        'form': form,
        'complaint': complaint,
        'media_files': complaint.media_files.all(),
    })