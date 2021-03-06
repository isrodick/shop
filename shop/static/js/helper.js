$(function() {
	window.HELPER = {
		'render_flash_message': function(message, error) {
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
		},
		'update_basket_total_qty': function(qty) {
			var $sidebar = $('#sidebar-wrapper'),
				$basket_link = $sidebar.find('.basket-link');

			if (qty <= 0) {
				$basket_link.html('Basket');

				return;
			}

			var $badge = $('<span/>'),
				$badge = $badge.addClass('sidebar-badge'),
				$badge = $badge.html(qty);

			$basket_link.html('Basket ').append($badge);
		}
	};
});
