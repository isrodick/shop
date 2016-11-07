$(function() {
	$(".confirm-delete").on('click', '.btn-ok', function(ev) {
		var $flash_message_block = $('.flash-message-block'),
			$modal = $(this).closest('.modal'),
			$delete_btn = $('[data-target="#' + $modal.attr('id') + '"]'),
			url = $delete_btn.data('href');

		$.ajax({
			url: url,
			type: "POST",
		}).done(function(data, status, xhr) {
			if (data.redirect_url) {
				location.href = data.redirect_url;

				return;
			}

			var message = data.message,
				_status = data.status;

			if (_status == 'error') {
				message = message || 'Error';
				$delete_btn.trigger('delete.error', data);
			} else {
				$delete_btn.trigger('delete.success', data);
			}

			if (message) {
				HELPER.render_flash_message(message, _status);
			}

			$modal.modal('hide');
		}).fail(function(data, status, xhr) {
			HELPER.render_flash_message(status, 'error');

			$modal.modal('hide');

			$delete_btn.trigger('delete.error', data);

			return;
		});
	});
});
