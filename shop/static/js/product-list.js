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

	$('.container-fluid').on('click', '.add-product', function(ev) {
		$.ajax({
			url: $(this).data('url'),
			type: "POST",
		}).done(function(data, status, xhr) {
			if (data.total_products_qty) {
				var $sidebar = $('#sidebar-wrapper'),
					$basket_link = $sidebar.find('.basket-link');

				var $badge = $('<span/>'),
					$badge = $badge.addClass('sidebar-badge'),
					$badge = $badge.html(data.total_products_qty);

				$basket_link.html('Basket ').append($badge);
			}

			if (data.status == 'error') {
				render_flash_message(data.message || 'Error', data.status);
			}
		}).fail(function(data, status, xhr) {
			render_flash_message(status, 'error');

			return;
		});
	});
});
