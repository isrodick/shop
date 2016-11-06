$(function() {
	$('.container-fluid').on('click', '.add-product', function(ev) {
		var $btn = $(this);

		$.ajax({
			url: $(this).data('url'),
			type: "POST",
		}).done(function(data, status, xhr) {
			if (data.total_products_qty) {
				var $sidebar = $('#sidebar-wrapper'),
					$basket_link = $sidebar.find('.basket-link'),
					$panel_heading = $btn.closest('.panel-heading');

				var $badge = $('<span/>'),
					$badge = $badge.addClass('sidebar-badge'),
					$badge = $badge.html(data.total_products_qty);

				$basket_link.html('Basket ').append($badge);

				var $label = $('<span/>'),
					$label = $label.addClass('label').addClass('label-info'),
					$label = $label.html('The product in the basket');

				$panel_heading.html($label);
			}

			if (data.status == 'error') {
				HELPER.render_flash_message(data.message || 'Error', data.status);
			}
		}).fail(function(data, status, xhr) {
			HELPER.render_flash_message(status, 'error');

			return;
		});
	});
});
