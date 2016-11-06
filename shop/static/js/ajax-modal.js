$(function() {
	function render_flash_message(message, error) {
		var $flash_message_block = $('.flash-message-block'),
			_class = (error == 'error')?  'alert-danger':'alert-warning';

		var $span = $('<span/>'),
			$span = $span.attr('aria-hidden', 'true'),
			$span = $span.html('×');

		var $close_btn = $('<button/>'),
			$close_btn = $close_btn.attr('type', 'button'),
			$close_btn = $close_btn.addClass('close'),
			$close_btn = $close_btn.attr('data-dismiss', 'alert').data('dismiss', 'alert'),
			$close_btn = $close_btn.attr('aria-label', 'Close'),
			$close_btn = $close_btn.html($span);

		var $div = $('<div/>'),
			$div = $div.addClass('alert').addClass(_class),
			$div = $div.attr('role', 'alert'),
			$div = $div.html($close_btn),
			$div = $div.append(message);

		$flash_message_block.append($div);
	};

	$("#confirm-delete").on('click', '.btn-ok', function(ev) {
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

			if (data.status == 'error') {
				message = message || 'Error';
			}

			if (message) {
				render_flash_message(message, _status);
			}

			$modal.modal('hide');
		}).fail(function(data, status, xhr) {
			render_flash_message(status, 'error');

			$modal.modal('hide');

			return;
		});
	});
});
