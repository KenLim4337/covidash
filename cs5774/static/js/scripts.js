const commentTemplate = `
    <li data-id="">
        <div class="upvotes" data-id="">
            <div class="chev-up"></div>
            <div class="vote-number">0</div>
            <div class="chev-down"></div>
        </div>
        <!--Icon from freeicons.io-->
        <div class="user-icon">
            <a href="">
                <img src="/static/img/user-icon.png" alt="User Icon">
            </a>
        </div>
        <div class="comment-body">
            <div class="user-name">
                <a href=""></a>
            </div>
            <div class="comment-text">
                <div class="body"></div>
                <div class="meta">
                    <p class="postdate">Posted: <em></em></p>
                </div> 
            </div>
            <div class="comment-controls" data-id="">
                <a href="#" class="edit-btn">Edit</a>
                <a href="#" class="delete-btn" >Delete</a>
            </div>
        </div>
    </li>
`

const editCommentTemplate = `
    <form action="#" class="comment-edit-form form-dark" data-id=0 >
        <textarea name="newComment" id="newComment" required></textarea>
        <input type="submit" value="Edit" date-id=0 >
    </form>
`

const deleteBox = '<div class="delete-box"><div class="delete-inner"><div class="delete-head">Really delete "<span class="delete-title"></span>"?</div><div class="delete-buttons"><button class="delete-yes">Yes</button><button class="delete-no">No</button></div></div></div><div class="delete-overlay"></div>'


//Cart popup content
const cartPopContent = {
    'add': '<div>You have successfully added <strong>"<span class="item-title"></span>"</strong> to your pending modules!</div>',
    'remove': '<div>You have successfully removed <strong>"<span class="item-title"></span>"</strong> from your pending modules!</div>',
    'removecart': '<div>You have successfully removed <strong>"<span class="item-title"></span>"</strong> from your pending modules! <a href="#" class="popup-undo">Undo</a></div>'
}

//Cart popup
const cartPopUp = '<div class="cart-popup"><div class="popup-inner"><div class="popup-content"></div><div class="close"></div></div></div>'

//Bring back cart rendering function
const cartTemplate = `
    <li>
        <div class="thumb-wrap">
            <img src="" alt="">
        </div>
        <div class="cart-item-content">
            <div class="title"></div>
        </div>
        <div class="close">
        </div>
    </li>
`

$(document).ready(() => {
    //CSRF
    const csrftoken = getCookie('csrftoken');

    //Add comment, other events for details page
    if($('article').length > 0) {
        $('body').on('click','.article-comment-upload form input[type="submit"]', function(e){
            e.preventDefault();
            e.stopPropagation();

            //Check if comment is empty
            if($('.article-comment-upload #commentbody').val().length > 0) {
                $('.comment-add-error').remove();
                //Run Ajax
                $.ajax({
                    url: $(this).data('ajax-url'),
                    data: {
                        rumourid: $('.article-comment-upload #rumourid').val(),
                        commentbody: $('.article-comment-upload #commentbody').val()
                    },
                    type:'POST',
                    dataType: "json",
                    headers: {'X-CSRFToken': csrftoken}
                }).done(function(json){

                    //Add new comment
                    $('.article-comments ul').prepend(jsonToComment(json));

                    $('.article-comment-upload #commentbody').val('');
                    $('html,body').animate({
                        scrollTop: $('.comment-block').offset().top - 40
                    })

                    //Remove other highlights first
                    $('.article-comments ul li').removeClass('highlight-comment');

                    $('.article-comments ul li:eq(0)').addClass('highlight-comment');

                    setTimeout(function(){
                        $('.article-comments ul li').removeClass('highlight-comment');
                    },5000);

                    //Remove no result message if present
                    $('.article-comments .no-result').remove();
                    
                    $('.comment-block .accordion-head .comments-num').text($('.article-comments ul li').length)

                }).fail(function(xhr,status,errorThrown){
                    console.log("Error: " + errorThrown);
                })
            } else {
                $('.comment-add-error').remove();
                $('.article-comment-upload form .form-title').after('<div class="comment-add-error">Comment cannot be empty</div>')
            }
            
        });

        //Delete stuff
        $('body').on('click', '.article-comments ul li .delete-btn', function(e){
            e.preventDefault();
            e.stopPropagation();

            $('.delete-box, .delete-overlay').remove();

            var deleteid = $(this).parents('.comment-controls').data('id');
            var tempBox = $(deleteBox);

            tempBox.find('.delete-head').text("Really delete this comment?");
            
            tempBox.find('.delete-yes').attr('data-id', deleteid).removeClass('delete-yes').addClass('delete-comment-yes');

            $('body').append(tempBox);

            $('body').addClass('showDelete');
        });

        $('body').on('click', '.delete-box .delete-comment-yes', function(e){
            e.preventDefault();
            e.stopPropagation();

            $('.delete-box, .delete-overlay').remove();

            var deleteid = $(this).data('id');

            $.ajax({
                url: '/rumours/remove-comment',
                data: {
                    id: deleteid,
                },
                type:'POST',
                dataType: "json",
                headers: {'X-CSRFToken': csrftoken}
            }).done(function(json){

                $('.article-comments ul li[data-id="'+json.id+'"]').remove();

                if($('.article-comments ul li').length == 0) {
                    $('.article-comments ul').append('<div class="no-result">No comments yet...</div>'); 
                }

                $('html,body').animate({
                    scrollTop: $('.comment-block').offset().top - 40
                })

                $('.comment-block .accordion-head .comments-num').text($('.article-comments ul li').length)
            }).fail(function(xhr,status,errorThrown){
                console.log("Error: " + errorThrown);
            })
        });

        //Edit Stuff
        $('body').on('click', '.article-comments ul li .edit-btn', function(e){
            e.preventDefault();
            e.stopPropagation();

            $('.article-comments ul li .comment-text, .article-comments ul li .comment-controls').show();
            $('.article-comments ul li .comment-edit-form').remove();

            var wrapper = $(this).parents('li');
            var template = $(editCommentTemplate)
            var editid = $(this).parents('.comment-controls').data('id');
            var currentComment = wrapper.find('.comment-text .body').text();

            template.find('textarea').text(currentComment);
            
            template.attr('data-id', editid);
            
            template.find('input[type="submit"]').attr('data-id', editid);
            
            wrapper.find('.comment-text, .comment-controls').hide();

            wrapper.find('.comment-body').append(template);
        });

        
        $('body').on('click', '.article-comments ul li .comment-edit-form input[type="submit"]', function(e){
            e.preventDefault();
            e.stopPropagation();

            var editid = $(this).data('id');
            var newbody = $(this).parent().find('#newComment').val();

            if(newbody.length > 0) {
                $('.comment-error').remove();

                $.ajax({
                    url: '/rumours/edit-comment',
                    data: {
                        id: editid,
                        body: newbody
                    },
                    type:'POST',
                    dataType: "json",
                    headers: {'X-CSRFToken': csrftoken}
                }).done(function(json){
    
                    var targetid = json.id;
                    var targetbody = json.body;
                    var targettime = json.time;
    
                    $('.article-comments ul li .comment-text, .article-comments ul li .comment-controls').show();
                    $('.article-comments ul li .comment-edit-form').remove();
    
                    $('.article-comments ul li[data-id="'+targetid+'"] .comment-text .body').text(targetbody);
    
                    if($('.article-comments ul li[data-id="'+targetid+'"] .meta .editdate').length > 0) {
                        $('.article-comments ul li[data-id="'+targetid+'"] .meta .editdate em').text(targettime);
                    } else {
                        $('.article-comments ul li[data-id="'+targetid+'"] .meta').append('<p class="editdate">Last Edit: <em>'+targettime+'</em></p>')
                    }

                    //Remove other highlights first
                    $('.article-comments ul li').removeClass('highlight-comment');
    
                    $('.article-comments ul li[data-id="'+targetid+'"]').addClass('highlight-comment');
    
                    setTimeout(function(){
                        $('.article-comments ul li').removeClass('highlight-comment');
                    },5000);
                }).fail(function(xhr,status,errorThrown){
                    console.log("Error: " + errorThrown);
                })
            } else {
                $('.comment-error').remove();
                $(this).parent().find('#newComment').before('<div class="comment-error">New comment cannot be empty</div>')
            }
        });

    }

    //Pie stuff
    if($('.validation-charts').length > 0) {
        refreshPies();
    }

    //Voting Ajax
    $('.vote-submit.blue-cta').click(function(){
        if($('#votetrue').val()) {
            //Remove messages
            $('.vote-error, .vote-success').remove();

            //Run Ajax
            $.ajax({
                url: $(this).data('ajax-url'),
                data: {
                    id: $('#votetrue').data('id'),
                    validity: $('#votetrue').val()
                },
                type:'POST',
                dataType: "json",
                headers: {'X-CSRFToken': csrftoken}
            }).done(function(json){
                var trueNum = json.true;
                var falseNum = json.false;
                var totalNum = trueNum + falseNum;
                var validity = json.validity;

                $('.validation-numbers .usernum').text(totalNum);
        
                $('.validation-charts .user-chart').data('true', trueNum);

                $('.validation-charts .user-chart').data('false', falseNum);

                //Add succ message
                $('#votetrue').after('<div class="vote-success">Successfully cast your vote!</div>');
                
                refreshPies();

                var valHtml = {
                    'True': '<span class=\'tick\'></span><span>True</span>',
                    'False': '<span class=\'cross\'></span><span>False</span>',
                    'Mixed': '<span class=\'mixed\'></span><span>Mixed</span>'
                }

                //Tweak validity item if different
                if($('.article-meta .validity').text().indexOf(validity) == -1) {
                    $('.article-meta .validity').html(valHtml[validity])
                }

            }).fail(function(xhr,status,errorThrown){
                console.log("Error: " + errorThrown);
            })
        } else {
            $('.vote-error, .vote-success').remove();
            $('#votetrue').after('<div class="vote-error">Please select a validity</div>')
        }
    });


    //Sort Stuff on load, disable active sort
    $('.sort-options li[data-sortby="'+$('.active-sort .sort-text').text().trim().toLowerCase()+'"]').addClass('disabled');

    $('.active-sort').click(function(){
        if($('.active-sort .chev-down').length > 0) {
            $('.sort-options').slideDown();
            $('.active-sort .chev-down').addClass('chev-up').removeClass('chev-down');
        } else {
            $('.sort-options').slideUp();
            $('.active-sort .chev-up').addClass('chev-down').removeClass('chev-up');
        }
    });

    //Sort event
    $('.sort-options li').click(function(){
        if(window.location.href.indexOf($(this).data('sortby')) == -1) {
            if(window.location.href.indexOf('&sortby') > -1) {
                window.location = window.location.href.split('&sortby')[0]+"&sortby="+$(this).data('sortby');
            } else if (window.location.href.indexOf('?searchquery') > -1) {
                window.location = window.location.href+"&sortby="+$(this).data('sortby');
            } else {
                window.location = window.location.href.split('?sortby')[0]+"?sortby="+$(this).data('sortby');
            }
        }
    }); 

    //Hide message
    if($('.dbMessage')) {
        setTimeout(function(){
            $('.dbMessage').slideUp(function(){
                $('.dbMessage').remove();
            });
        }, 8000);
    }

    /*Delete stuff*/
    $('body').on('click', 'form.delete-form input[type="submit"]', function(e){
        //Prevent form submission and add box
        e.preventDefault();
        e.stopPropagation();
        $('.delete-box, .delete-overlay').remove();

        var tempBox = $(deleteBox);

        tempBox.find('.delete-title').text($(this).parents('form.delete-form').attr('data-title'));
        tempBox.find('.delete-yes').attr('data-id', $(this).parents('form.delete-form').attr('data-id'));

        $('body').append(tempBox);
        $('body').addClass('showDelete');
    });
    
    //Delete buttons
    $('body').on('click', '.delete-yes', function(e){
        $('form.delete-form[data-id='+$(this).attr('data-id')+']').submit();
        $('.delete-box, .delete-overlay').remove();
        $('body').removeClass('showDelete');
    });

    $('body').on('click', '.delete-no, .delete-overlay', function(e){
        $('.delete-box, .delete-overlay').remove();
        $('body').removeClass('showDelete');
    });

    /*Set active nav link*/
    $('nav ul li a').removeClass('current');
    $('nav ul li a[href="'+window.location.pathname+'"]').addClass('current');

    //Cart events
    //Initialize cart storage item
    var cart = JSON.parse(sessionStorage.getItem('coviCart')) || [];

    //Set number of cart items
    $('header .header-inner .cart-wrap .cart-link .cart-number').text(cart.length);

    //Cart length
    if (document.location.pathname.indexOf('cart') > -1) {
        var cart = JSON.parse(sessionStorage.getItem('coviCart')) || [];

        $('.cart-section .cart-number').text(cart.length);

        //Handle cart on load
        $.ajax({
            url: '/cart/cart-render',
            data: {
                'cartData[]': cart
            },
            type:'POST',
            dataType: "json",
            headers: {'X-CSRFToken': csrftoken}
        }).done(function(json){
            var items = JSON.parse(json.results);
            populateCart('#cart', items);
        }).fail(function(xhr,status,errorThrown){
            console.log("Error: " + errorThrown);
        })

        if(cart.length == 0) {
            //If no items in cart
            $('.cart-section .cart-inner #cart').after('<div class="no-result">Nothing to see here...</div>');

            $('.cart-section .cart-inner #cart, .cart-section .cart-cta').hide();
        } else {
            $('.cart-section .cart-inner #cart, .cart-section .cart-cta').show();
            $('#cart li').hide();
            cart.forEach(function(e){
                $('#cart li[data-id="'+e+'"]').show();
            });
        }
    }

    //Handle home and list on load
    if ($('.module-group-wrapper').length > 0) {
        if(cart.length !== 0) {
            cart.forEach(function(e){
                $('.tile-cta .to-cart[data-id='+e+']').addClass('remove-cart').removeClass('to-cart').text('Remove');
            });
        }

        $('.module-group-wrapper').each(function(e){
            var index = 1; 
            $(this).find('.module-tile').each(function(f){
                //Index the tile
                $(this).addClass('tile'+index);

                if(index < 4) {
                    index++;
                } else {
                    index=1;
                }
            });
        });
    }

    //Stores settimeout
    var popPoller;
    var removePoller;

    //Add to cart button
    $('body').on('click', '.to-cart', function (e) {
        e.preventDefault();
        e.stopPropagation();
        cart.push($(this).data('id'));
        $(this).addClass('remove-cart').removeClass('to-cart').text('Remove');
        sessionStorage.setItem('coviCart', JSON.stringify(cart));
        $('header .header-inner .cart-wrap .cart-link .cart-number').text(cart.length);

        //Edit and show cart popup
        var tempPop = $(cartPopUp);
        
        var tempCont = $(cartPopContent.add);

        tempCont.find('.item-title').append($($(this).parents('.module-tile')).find('.title').text());
        tempPop.find('.popup-content').html(tempCont);

        jQuery('.cart-popup').remove();
        jQuery('body').append(tempPop);

        setTimeout(function(){
            jQuery('body').addClass('show-cart-pop');
        },50);
        //Reset timeout if a new message is shown
        clearTimeout(popPoller);
        clearTimeout(removePoller);
        popPoller = setTimeout(function () {
            jQuery('body').removeClass('show-cart-pop');
            removePoller = setInterval(function(){
                jQuery('.cart-popup').remove();
            },300);
        }, 3000);
    });

    //Remove from cart button
    $('body').on('click', '.remove-cart', function (e) {
        e.preventDefault();
        e.stopPropagation();
        cart.splice(cart.indexOf($(this).data('id')), 1);
        $(this).addClass('to-cart').removeClass('remove-cart').text('Add to Dashboard');
        sessionStorage.setItem('coviCart', JSON.stringify(cart));
        $('header .header-inner .cart-wrap .cart-link .cart-number').text(cart.length);

        //Edit and show cart popup
        var tempPop = $(cartPopUp);
                
        var tempCont = $(cartPopContent.remove);

        tempCont.find('.item-title').append($($(this).parents('.module-tile')).find('.title').text());
        tempPop.find('.popup-content').html(tempCont);

        jQuery('.cart-popup').remove();
        jQuery('body').append(tempPop);

        setTimeout(function(){
            jQuery('body').addClass('show-cart-pop');
        },50);
        //Reset timeout if a new message is shown
        clearTimeout(popPoller);
        clearTimeout(removePoller);
        popPoller = setTimeout(function () {
            jQuery('body').removeClass('show-cart-pop');
            removePoller = setInterval(function(){
                jQuery('.cart-popup').remove();
            },300);
        }, 3000);


    });

    //Cart page remove from cart
    $('body').on('click', '#cart li .close', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var id = $(this).parents('li').data('id');
        cart.splice(cart.indexOf(id), 1);
        sessionStorage.setItem('coviCart', JSON.stringify(cart));
        $('header .header-inner .cart-wrap .cart-link .cart-number').text(cart.length);
        $('.cart-section .cart-number').text(cart.length);
        $(this).parents('li').remove();

        //if cart is emptied, add empty cart message
        if (cart.length == 0) {
            $('.cart-section .cart-inner').append('<div class="no-result">Nothing to see here...</div>');
            $('.cart-section .cart-inner #cart, .cart-section .cart-cta').hide();
        }
        
        //Edit and show cart popup
        var tempPop = $(cartPopUp);
                
        var tempCont = $(cartPopContent.removecart);

        tempCont.find('.item-title').append($($(this).parents('li')).find('.title').text());
        tempCont.find('.popup-undo').attr('data-id', id);

        tempPop.find('.popup-content').html(tempCont);

        jQuery('.cart-popup').remove();
        jQuery('body').append(tempPop);

        setTimeout(function(){
            jQuery('body').addClass('show-cart-pop');
        },50);
        //Reset timeout if a new message is shown
        clearTimeout(popPoller);
        clearTimeout(removePoller);
        popPoller = setTimeout(function () {
            jQuery('body').removeClass('show-cart-pop');
            removePoller = setInterval(function(){
                jQuery('.cart-popup').remove();
            },300);
        }, 6000);

    });

    //Cart popup undo
    $('body').on('click', '.cart-popup .popup-undo', function (e) {
        e.preventDefault();
        e.stopPropagation();

        cart.push($(this).data('id'));
        sessionStorage.setItem('coviCart', JSON.stringify(cart));
        jQuery('body').removeClass('show-cart-pop');

        $('.cart-section .cart-number').text(cart.length);
        $('header .header-inner .cart-wrap .cart-link .cart-number').text(cart.length);

        //Undo item removal
        $.ajax({
            url: '/cart/cart-undo',
            data: {
                'prodId': $(this).data('id')
            },
            type:'POST',
            dataType: "json",
            headers: {'X-CSRFToken': csrftoken}
        }).done(function(json){
            var toAdd = $(cartTemplate);

            //In the case of undo there will always only be one item
            var item = JSON.parse(json.results)[0];

            //Image
            toAdd.find('.thumb-wrap img').attr('src', item.fields.img).attr('alt', item.fields.title);

            //Title and category
            toAdd.find('.cart-item-content .title').text(item.fields.title);

            //Add id to cart tile
            toAdd.attr('data-id', item.pk);

            $('#cart').append(toAdd);
            
            $('.cart-section .cart-inner #cart, .cart-section .cart-cta').show();
            $('.cart-section .cart-inner .no-result').remove();

            //Edit and show cart popup
            var tempPop = $(cartPopUp);
            
            var tempCont = $(cartPopContent.add);

            tempCont.find('.item-title').append(item.fields.title);
            
            tempPop.find('.popup-content').html(tempCont);

            jQuery('.cart-popup').remove();
            jQuery('body').append(tempPop);

            setTimeout(function(){
                jQuery('body').addClass('show-cart-pop');
            },50);
            //Reset timeout if a new message is shown
            clearTimeout(popPoller);
            clearTimeout(removePoller);
            popPoller = setTimeout(function () {
                jQuery('body').removeClass('show-cart-pop');
                removePoller = setInterval(function(){
                    jQuery('.cart-popup').remove();
                },300);
            }, 3000);

        }).fail(function(xhr,status,errorThrown){
            console.log("Error: " + errorThrown);
        })
    });

    //Cart popup close
    $('body').on('click', '.cart-popup .close', function () {
        jQuery('body').removeClass('show-cart-pop');
    });

    //Hamburger 
    $('header .hamburger').click(function (e) {
        e.preventDefault();
        e.stopPropagation();
        $('body').toggleClass('mobile-menu-active');

        if($('body').hasClass('mobile-menu-active')) {
            $('body').append('<div class="hamburger-overlay"></div>');
        } else {
            $('.hamburger-overlay').remove();
        }
    });

    $('body').on('click','.hamburger-overlay', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $('body').removeClass('mobile-menu-active');
        $('.hamburger-overlay').remove();
    });

    //Accordions
    $('.accordion-head').click(function (e) {
        //Currently open
        if ($(this).find('.chev-up').length > 0) {
            $(this).find('.chev-up').addClass('chev-down').removeClass('chev-up');
            $(this).next().slideUp();
        } else {
            //closed
            $(this).find('.chev-down').addClass('chev-up').removeClass('chev-down');
            $(this).next().slideDown();
        }
    })

    //Resize event
    var windowWidth = $(window).width();

    $(window).resize(function (e) {
        if ($(window).width() < 769 && windowWidth > 768) {
            //Hide all but the first footer accordion when sizing down from desktop
            windowWidth = $(window).width();
            $('footer .accordion-head').next().hide();
            $('footer .accordion-head [class*="chev"]').addClass('chev-down').removeClass('chev-up');

            $('footer .accordion-head:eq(0)').next().show();
            $('footer .accordion-head:eq(0) [class*="chev"]').addClass('chev-up').removeClass('chev-down');

        } else if ($(window).width() > 768 && windowWidth < 769) {
            windowWidth = $(window).width();
            //Reopen all accordions in the footer when going back to desktop
            $('footer .accordion-head').next().show();
            $('footer .accordion-head [class*="chev"]').addClass('chev-up').removeClass('chev-down');
        }
    });

    //On pageload
    if (windowWidth < 769) {
        //Hide all but the first footer accordion when sizing down from desktop
        $('footer .accordion-head').next().hide();
        $('footer .accordion-head [class*="chev"]').addClass('chev-down').removeClass('chev-up');

        $('footer .accordion-head:eq(0)').next().show();
        $('footer .accordion-head:eq(0) [class*="chev"]').addClass('chev-up').removeClass('chev-down');
    }
})

//Update pie charts and validity info based on data
function refreshPies() {
    $('.validation-charts > div').each(function(){
        var target = $(this);
        var truenum = target.data('true');
        var falsenum = target.data('false');

        if(truenum + falsenum !== 0) {
            var fpercent = (falsenum/(truenum+falsenum)) * 100;

            target.find('.pie').css('background', 'conic-gradient(#bb3333 0, #bb3333 '+fpercent+'%, #33aa33 0, #33aa33 100%)')
    
            if (fpercent == 50) {
                target.find('.percentage strong').text('Mixed');
                target.find('.percentage .percent-number').text(fpercent.toFixed(0)+'%');
            } else if (fpercent < 50) {
                target.find('.percentage strong').text('True');
                target.find('.percentage .percent-number').text((100 - fpercent).toFixed(0)+'%');
            } else {
                target.find('.percentage strong').text('False');
                target.find('.percentage .percent-number').text(fpercent.toFixed(0)+'%');
            }
        } else {
            target.find('.pie').css('background', 'conic-gradient(#bb3333 0, #bb3333 50%, #33aa33 0, #33aa33 100%)')
            
            target.find('.percentage strong').text('No Data');
            target.find('.percentage .percent-number').text('');
        }
    });
}

//Populate a cart based on a json list of rumours
function populateCart(selector, itemList) {
    $('.cart-section .cart-inner #cart, .cart-section .cart-cta').show();
    $('.cart-section .cart-inner .no-result').remove();

    if (itemList.length > 0) {
        itemList.forEach(function(e) {
            var toAdd = $(cartTemplate);

            var tempData = e;

            //Image
            toAdd.find('.thumb-wrap img').attr('src', tempData.fields.img).attr('alt', tempData.fields.title);

            //Title and category
            toAdd.find('.cart-item-content .title').text(tempData.fields.title);

            //Add id to cart tile
            toAdd.attr('data-id', e.pk);

            $(selector).append(toAdd);
        });
    } else {
        //If no items in cart
        $(selector).after('<div class="no-result">Nothing to see here...</div>');

        $('.cart-section .cart-inner #cart, .cart-section .cart-cta').hide();
    }

}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function jsonToComment(json) {
    var commentData = json;
    var newComment = $(commentTemplate);

    console.log(commentData.id);

    newComment.attr('data-id', commentData.id);
    
    newComment.find('.upvotes, .comment-controls').attr('data-id', commentData.id);

    newComment.find('.user-icon a, .user-name a').attr('href', commentData.commenterUrl);
    
    newComment.find('.user-name a').after(' | ' + commentData.commenterTitle);

    newComment.find('.user-name a').text(commentData.commenter);

    newComment.find('.comment-text .body').text(commentData.body);

    newComment.find('.meta .postdate em').text(commentData.time);

    return newComment;
}
