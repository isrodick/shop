$(function() {
	$('.product-item').on('click', '.btn-number', function(ev) {
		var $input = $($(this).data('target')),
			btn_type = $(this).data('type'),
			qty = $input.val();

		if (btn_type == 'plus') {
			$input.val(++qty);
		} else if (btn_type == 'minus') {
			$input.val(--qty);
		}

		$.ajax({
			url: $input.data('url'),
			type: "POST",
			data: {
				qty: qty
			}
		}).done(function(data, status, xhr) {
			var $form_group = $input.closest('.form-group'),
				$errors_row = $form_group.find('.errors');

			$form_group.removeClass('has-error');
			$errors_row.empty();

			if (data.total_products_qty) {
				var $sidebar = $('#sidebar-wrapper'),
					$basket_link = $sidebar.find('.basket-link');

				var $badge = $('<span/>'),
					$badge = $badge.addClass('sidebar-badge'),
					$badge = $badge.html(data.total_products_qty);

				$basket_link.html('Basket ').append($badge);
			}

			if (data.status == 'error') {
				HELPER.render_flash_message(data.message || 'Error', data.status);
			} else if (data.status == 'valid-error') {
				var $errors_row = $form_group.find('.errors');

				var $error_p = $('<p/>'),
					$error_p = $error_p.addClass('error'),
					$error_p = $error_p.html(data.message || 'Validation error');

				$form_group.addClass('has-error');

				$errors_row.html($error_p);
			}
		}).fail(function(data, status, xhr) {
			HELPER.render_flash_message(status, 'error');

			return;
		});
	});
});
