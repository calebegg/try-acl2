sid = Math.random();
current_section = 0;
function on_resize() {
  pre_width = pre.width();
  if (pre_width > 800) {
    // An awful kludge to wait for the font to load. :-(
    setTimeout(on_resize, 100);
    return;
  }
  outer_console.width(pre_width + 10);
  tutorial.width(body.width() - pre_width + 10);
  info.css('right', pre_width - info.width() - 35 + 'px');
  jq_console.height(outer_console.height() - $('h1').height() - 10);
}
window.onresize = on_resize;
opacity = 0;
function showPrevSection() {
  if (current_section === 0) {
    return;
  } else {
    current = sections.eq(current_section);
    current.hide();
    current_section--;
    current = sections.eq(current_section);
    current.show();
    if (current.parent().is(':hidden')) {
      $('article:visible').hide()
      current.parent().show()
    }
  }
}
function showNextSection() {
  if (current_section >= sections.length - 1) {
    return;
  } else {
    sections.eq(current_section).hide();
    current_section++;
    current = sections.eq(current_section);
    current.show();
    if (current.parent().is(':hidden')) {
      $('article:visible').hide()
      current.parent().show()
    }
  }
}
function main() {
  // Globals
  jq_console = $('#jq-console');
  outer_console = $('#console');
  console_inner = $('.jquery-console-inner');
  pre = $('#ref');
  body = $('body');
  tutorial = $('#tutorial');
  info = $('aside');
  articles = $('#tutorial article');
  sections = $('#tutorial article section');
  throbber = $('#throbber');
  on_resize();
  // Set up tutorial
  articles.eq(0).show();
  sections.eq(0).show();
  $('#prev').click(showPrevSection);
  $('#next').click(showNextSection);
  // Shadow effect on scrolled console
  function consoleShadowScrollHandler() {
    if (this.scrollTop > 0) {
      old_opacity = opacity;
      opacity = Math.min(this.scrollTop, 20) / 20 / 6 + .05;
      if (opacity != old_opacity) {
        outer_console.css('box-shadow', "2px 2px 8px rgba(0, 0, 0, .2), " +
          " 0 15px 10px -10px rgba(0,0,0," + opacity + ") inset");
      }
    } else {
      outer_console.css('box-shadow', '');
    }
  }
  outer_console.scroll(consoleShadowScrollHandler);
  controller = jq_console.console(
    {
      autofocus: true,
      promptLabel: '> ',
      continuedPromptLabel: '... ',
      commandValidate: function(line) {
        if (line === "") {
          return false;
        } else {
          return true;
        }
      },
      commandHandle: function(line, report) {
        paren_count = parens_match(line);
        if (paren_count > 0) {
          controller.continuedPrompt = true;
          indent = '';
          for (i = 0; i < paren_count - 1; i++) {
            indent += '  ';
          }
          controller.setContinuedPromptLabel('... ' + indent);
          return;
        } else if (paren_count < 0) {
          controller.continuedPrompt = false;
          report([{msg:"Unmatched ')'", className:"error"}]);
          return;
        }
        throbber.show();
        controller.continuedPrompt = false;
        $.get('', {code: line, sid: sid}, function(data) {
          data = data.trim();
          collapse_box = $('<div class="collapse"></div>');
          collapse_box.click(function() {
            $($(this).children()[1]).toggle(1);
          });
          collapse_box.append(message = $('<div>'));
          collapse_box.append($('<div>')
                                .text(data)
                                .hide()
                                .addClass('jquery-console-message'));
          if (data.match('FAILED')) {
            message.text('Failed. (click for details)').addClass('failure');
            report(collapse_box);
          } else if (data.match('Proof succeeded.') || data.match('trivial') ||
              data.match('Q\\.E\\.D\\.')) {
            message.text('Succeeded. (click for details)').addClass('success');
            report(collapse_box);
          } else{
            report(data);
          }
          jq_console.css('opacity', '1');
          throbber.hide();
          outer_console_elem = outer_console[0];
          outer_console_elem.scrollTop = outer_console_elem.scrollHeight;
        });
      }
  });
  $('code').each(function() {
    $(this).click(function() {
      controller.promptText($(this).text());
      controller.inner.click();
    });
  });
}
$(main);
function parens_match(line) {
  // Remove string literals
  line = line.replace(/"([^"]|\\")*?"/g, "")
  // Remove pipe symbols
  line = line.replace(/\|[^\|]*?\|/g, "")
  opens = line.match(/\(/g);
  open_cnt = (opens ? opens.length : 0);
  closes = line.match(/\)/g);
  close_cnt = (closes ? closes.length : 0);
  if (line.match(/"/g) || line.match(/\|/g)) {
    // Unterminated string
    return 1 + open_cnt - close_cnt;
  }
  return open_cnt - close_cnt;
}
