$(function() {
	var $total_price = $('span#total-price');

	function render_error($form_group, $errors_row, message) {
		var $error_p = $('<p/>'),
			$error_p = $error_p.addClass('error'),
			$error_p = $error_p.html(message);

		$form_group.addClass('has-error');

		$errors_row.html($error_p);
	};

	$('.product-item').on('click', '.btn-number', function(ev) {
		var $form_group = $(this).closest('.form-group'),
			$errors_row = $form_group.find('.errors'),
			$btn_plus = $form_group.find('button[data-type="plus"]'),
			$btn_minus = $form_group.find('button[data-type="minus"]'),
			$input = $($(this).data('target')),
			btn_type = $(this).data('type'),
			qty = $input.val().trim(),
			max = $input.data('max');

		if ( !(/^\d+$/.test(qty)) ) {
			render_error($form_group, $errors_row, 'Please enter integer value');

			$input.val(qty);

			return;
		}

		if (btn_type == 'plus') {
			$input.val(++qty);
		} else if (btn_type == 'minus') {
			$input.val(--qty);
		}

		if (qty >= max) {
			$btn_plus.attr('disabled', true);
		} else {
			$btn_plus.attr('disabled', false);
		}

		if (qty > 1) {
			$btn_minus.attr('disabled', false);
		} else {
			$btn_minus.attr('disabled', true);
		}

		$.ajax({
			url: $input.data('url'),
			type: "POST",
			data: {
				qty: qty
			}
		}).done(function(data, status, xhr) {
			if (data.status == 'error') {
				HELPER.render_flash_message(data.message || 'Error', data.status);
			} else if (data.status == 'valid-error') {
				render_error($form_group, $errors_row, data.message || 'Validation error');
			} else {
				$form_group.removeClass('has-error');
				$errors_row.empty();

				if (data.total_products_qty) {
					HELPER.update_basket_total_qty(data.total_products_qty);
				}

				if ('total_price' in data) {
					$total_price.html(data.total_price);
				}
			}
		}).fail(function(data, status, xhr) {
			HELPER.render_flash_message(status, 'error');

			return;
		});
	});
});
