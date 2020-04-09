#!/usr/bin/perl
#mihael.arcan@deri.org

use strict;
use warnings;
use Data::Dumper;
use Benchmark;

use Encode;
use utf8;
#binmode(STDIN, ":utf8");
binmode(STDOUT, ":utf8");


my $t0 = new Benchmark;

use URI::Escape;
use File::Temp qw/ tempfile tempdir /;

my $moses_dir = "/home/tools/mosesdecoder";

my $dir = tempdir(DIR => "/tmp", CLEANUP =>  0 );
`mkdir $dir -p`;
`chmod -R 777 $dir`;

my @list;
read(STDIN, my $entry, $ENV{'CONTENT_LENGTH'});

my ($lang) = $entry =~ /name="lang"\s+(.*?)\r\n----/s;


print "Content-type: text/html\n\n";
my $en_header = <<"END_MESSAGE";
<!doctype html>
<html lang="en">
	<head>
		<meta charset="utf-8" />
		<title>IRIS | English-Irish Translation System</title>
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css">
		<link rel="stylesheet" href="../style.css" />
		<link rel="stylesheet" href="../iris.css" />

		<!--[if IE]>
		<script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
		<![endif]-->

	</head>
	<body>
		<header>
		
			<div class="container">
				
				<div class="alighleft">
					<span class="logo"><span class="green">IRIS</span></span>
					English-Irish Translation System
				</div>

				<ul class="alighright">
					<li><a href="../"><i class="fa fa-home"></i> Home</a></li>
					<li><a href="../inneacs.html">☘ Irish</a></li>
					<li><a href="../about.html"><i class="fa fa-comment"></i> About</a></li>
					<li><a href="../team.html"><i class="fa fa-users"></i> Team</a></li>
					<li><a href="../docker.html"><i class="fa fa-cogs"></i> Docker</a></li>
					<li>
						<a href="#"><i class="fa fa-tags"></i> Other Projects</a>
						<ul>
							<li><a href="../../iris/" target="_top">IRIS</a></li>
							<li><a href="../../otto/" target="_top">OTTO</a></li>
							<li><a href="../../asistent/" target="_top">Asistent</a></li>
							<li><a href="../../tetra/" target="_top">TeTra</a></li>
						</ul>
					</li>
				</ul>
				<div class="clear"></div>
				
			</div>

		</header>
		
		<div class="container">
			<div class="contentsfull">
END_MESSAGE

my $ga_header = <<"END_MESSAGE";
<!doctype html>
<html lang="ga">
	<head>
		<meta charset="utf-8" />
		<title>IRIS | English-Irish Translation System</title>
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.3.0/css/font-awesome.min.css">
		<link rel="stylesheet" href="../style.css" />
		<link rel="stylesheet" href="../iris.css" />

		<!--[if IE]>
		<script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script>
		<![endif]-->
	</head>
	<body>
		<header>
		
			<div class="container">
				
				<div class="alighleft">
					<span class="logo"><span class="green">IRIS</span></span>
					Córas Aistriúcháin Béarla-Gaeilge
				</div>

				<ul class="alighright">
					<li><a href="../innéacs.html"><i class="fa fa-home"></i> Baile</a></li>
					<li><a href="../index_en.html"><i class="fa fa-language"></i> Béarla</a></li>
					<li><a href="../faoi.html"><i class="fa fa-comment"></i> Maidir le</a></li>
					<li><a href="../foireann.html"><i class="fa fa-users"></i> Foireann</a></li>
					<li><a href="../docker.html"><i class="fa fa-cogs"></i> Docker</a></li>
					<li>
						<a href="#"><i class="fa fa-tags"></i> Tionscadail Eile</a>
						<ul>
							<li><a href="../../iris/" target="_top">Iris</a></li>
							<li><a href="../../otto/" target="_top">Otto</a></li>
							<li><a href="../../asistent/" target="_top">Asistent</a></li>
							<li><a href="../../tetra/" target="_top">Tetra</a></li>
						</ul>
					</li>
				</ul>
				<div class="clear"></div>
				
			</div>

		</header>
		
		<div class="container">
			<div class="contentsfull">
END_MESSAGE

if ($lang eq "english" ) {
	print $en_header;
} else {
	print $ga_header;
}





my ($text) = $entry =~ /form-data; name="Text"\s(.*?)\r\n----/s;
$text =~ s/^\s+//;
my ($method) = $entry =~ /form-data; name="method"\s+(.*?)\r\n----/s;


#print "$entry\n<br><br>"; #exit;
#print "|$lang|$method|"; #exit;


if (($text)) { ####&&($lang_id)
	my $model_path = "/var/www/models";
	$text =~ s/\n\r/\n/g;
	$text =~ s/\.\s/.\n/g if ($method eq "nmt");
	@{$list[0]} = split(/\n+/,$text);
	my $cpus = scalar (@{$list[0]});
	if (scalar (@{$list[0]}) > 4) {
		$cpus = 4;
	}
	foreach my $i (0 .. $#{$list[0]}) {
		$list[0][$i] =~ s/\+/ /g;
		$list[0][$i]  = uri_unescape($list[0][$i]);
	}
	my $string = 	join("\n",@{$list[0]});
	$string =~ s/"/'/g;
	$string =~ s/'/\'/g;
	

	if (scalar(@{$list[0]}) < 250) {
	
		my $l1; my $l2;
		my ($lang_id) = `echo "$string" | python /var/www/cgi-bin/langid.py`  =~ /\('(.+?)'/;
		if ($lang_id eq "en") {
			$l1 = "en";	
			$l2 = "ga";
		} elsif  ($lang_id = "ga") {
			$l1 = "ga";	
			$l2 = "en";
		}


		### hack
		if ($method eq "pbsmt") {

			unless (-f "$model_path/$method/tms/$l1\_$l2/moses.filtered.compact.tuned.ini") {
				`mkdir $model_path/$method/tms/$l1\_$l2 -p`;
				`mkdir $model_path/$method/lms -p`;
				`wget http://server1.nlp.insight-centre.org/mt_models/tms/tm_$l1\_$l2.tgz -P $model_path/$method/tms/$l1\_$l2/` unless (-f "$model_path/$method/tms/$l1\_$l2/models_$l1\_$l2.tgz");
				`wget http://server1.nlp.insight-centre.org/mt_models/lms/langm.$l2.kenlm.trie.tgz -P  $model_path/$method/lms/` unless (-f "$model_path/$method/lms/langm.$l2.kenlm.trie.tgz");
				`tar xfz $model_path/$method/tms/$l1\_$l2/tm_$l1\_$l2.tgz -C $model_path/$method/tms/$l1\_$l2/` unless (-f "$model_path/$method/tms/$l1\_$l2/phrase-table-filtered-compact.minphr");
				`tar xfz $model_path/$method/lms/langm.$l2.kenlm.trie.tgz -C $model_path/$method/lms` unless (-f "$model_path/$method/lm/langm.$l2.kenlm.trie");
				`rm $model_path/$method/tms/$l1\_$l2/tm_$l1\_$l2.tgz` if (-f "$model_path/$method/tms/$l1\_$l2/moses.filtered.compact.tuned.ini");
				`rm $model_path/$method/lms/langm.$l2.kenlm.trie.tgz` if (-f "$model_path/$method/lms/langm.$l2.kenlm.trie");
				open my $file_in, "<", "$model_path/$method/tms/$l1\_$l2/moses.filtered.compact.tuned.ini";
				undef $/; my $data = <$file_in>; $/ = "\n";
				$data =~ s/__PATH_TO__\/(.+?.minphr)/$model_path\/$method\/tms\/$l1\_$l2\/$1/;
				$data =~ s/__PATH_TO__\/(.+?.compact)/$model_path\/$method\/tms\/$l1\_$l2\/$1/;
				$data =~ s/__PATH_TO__\/(.+?.kenlm.trie)/$model_path\/$method\/lms\/$1/;
				open my $file_out, ">", "$model_path/$method/tms/$l1\_$l2/moses.ini";
				print $file_out $data;
				close($file_in); close($file_out);
			}
			@{$list[2]} = `echo "$string" | nice -n 7 ionice -c 2 -n 0 perl $moses_dir/scripts/tokenizer/tokenizer.perl -a -threads $cpus -l $l1 | nice -n 7 ionice -c 2 -n 0 perl $moses_dir/scripts/tokenizer/lowercase.perl | nice -n 7 ionice -c 2 -n 0 $moses_dir/bin/moses -f $model_path/$method/tms/$l1\_$l2/moses.ini -search-algorithm 1 -cube-pruning-pop-limit 500 -s 500 -n-best-list $dir/nbestlist.txt 10 distinct -v 0 -threads $cpus | nice -n 7 ionice -c 2 -n 0 $moses_dir/scripts/tokenizer/detokenizer.perl -u -l $l2`;
		} else {
			unless (-f "/var/www/models/nmt/$l1\_$l2\_latest.t7") {
					`mkdir -p /var/www/models/nmt/` unless (-d "/var/www/models/nmt/");
					`mkdir -p /var/www/models/bpes/` unless (-d "/var/www/models/bpes/");
		            `wget http://server1.nlp.insight-centre.org/mt_models/nmt/$l1\_$l2\_latest.tgz -O /var/www/models/nmt/$l1\_$l2\_latest.tgz`;
		            `tar xfz /var/www/models/nmt/$l1\_$l2\_latest.tgz -C /var/www/models/nmt/`;
		            `wget http://server1.nlp.insight-centre.org/mt_models/bpes/$l1.bpe32k -O /var/www/models/bpes/$l1.bpe32k`;
           	}
			@{$list[2]} = `echo "$string" | $moses_dir/scripts/tokenizer/lowercase.perl | /home/tools/CTranslate/lib/tokenizer/build/cli/tokenize --mode aggressive --bpe_model /var/www/models/bpes/$l1.bpe32k --joiner_annotate | /home/tools/CTranslate/build/cli/translate --disable_logs --model /var/www/models/nmt/$l1\_$l2\_latest.t7 --threads 4 | /home/tools/CTranslate/lib/tokenizer/build/cli/detokenize`; 
		}


		
		print "<table  width=\"100%\" border=\"0\">\n";
		my $width = "40";
		if ($lang eq "english") {
			print "<tr><td width=\"$width%\" style=\"text-align:center\"><b>Source language</b></td><td width=\"4%\"></td><td width=\"$width%\" style=\"text-align:center\"><b>Target language</b></td><td style=\"text-align:right\"><b>Optional transl.</b></td></tr>\n";
		} else {
			print "<tr><td width=\"$width%\" style=\"text-align:center\"><b>Bunteanga</b></td><td width=\"4%\"></td><td width=\"$width%\" style=\"text-align:center\"><b>Sprioctheanga</b></td><td style=\"text-align:right\"><b>Aistriúcháin bhreise 
</b></td></tr>\n";
		}
		print "</table>\n";
		print "<hr style=\"color:#FFFFFF;\">\n";
		print "<table width=\"100%\" border=\"0\">\n";
	
	
		my $size = 1;
		my $last = $#{$list[0]};
		foreach my $i (0 .. $#{$list[0]}) {
			if ($list[0][$i]) {
				$size++ if ($last == $i);
				$list[0][$i] =~ s/(\n|\r|\x0d)//g;
				$list[2][$i] =~ s/(\n|\r|\x0d)//g;
				$list[2][$i] =~ s/\s*\@-\@\s*/-/g;
				my $target = $list[2][$i];
				my $source = $list[0][$i];
				use Encode;
				utf8::decode($target);
				utf8::decode($source);

				print "<tr><td width=\"$width%\" style=\"text-align:justify\">$source</td><td width=\"4%\"><div style=\"text-align: center\">&#8594;</div></td><td width=\"$width%\" style=\"text-align:justify\">$target</td><td width=\"2%\"></td><td width=\"5%\">
						
						<form method=\"post\" action=\"get_n_best.cgi\" target=\"_blank\">
						<input type=\"submit\" name =\"$list[0][$i]|||$i|||$dir/nbestlist.txt\"  value=\"n-best\" >
						</form>
						</td>
						</tr><tr><td colspan=\"5\"><hr style=\"color:#FFFFFF;\" SIZE=\"$size\"></td></tr>\n";  #
				
			}
		}
		print "</table>\n";
#		print "<hr style=\"color:#FFFFFF;\">\n";
		print "<font size=\"2\">\n";

		my ($time) = timestr(timediff(new Benchmark, $t0)) =~ /(\d+) wallclock secs/;

		if ($lang eq "english") {
			print "<div style=\"text-align: center\">decoding  took $time seconds</div>\n";
		} else {
			print "<div style=\"text-align: center\">am le díchódú $time soicind</div>\n";
		}
		
		print "</font>\n";
		print "<br>\n";
	} else {
		if ($lang eq "english") {
			print "Due to the reserach environment, please reduce the data to be translated to 200 sentences. Please contact <a href=\"mailto:mihael.arcan\@insight-centre.org\">Mihael Arcan</a>, if you need to translate a larger amount of text. <br><br>\n";
		} else {
			print "Mar gheall ar an timpeallacht reserach, le do thoil a laghdú na sonraí atá le haistriú go 200 abairtí. Téigh i dteagmháil <a href=\"mailto:mihael.arcan\@insight-centre.org\">Mihael Arcan</a>, más gá duit a aistriú le méid níos mó de théacs. <br><br>\n";
		}
	}
} else {
	print "No text was added<br>";
}



if ($lang eq "english") {
	print "<div style=\"text-align: center\"><a href=\"../\" TARGET=\"_top\"><strong>Back to homepage</strong></strong</a></div>";
} else {
	print "<div style=\"text-align: center\"><a href=\"../innéacs.html\" TARGET=\"_self\"><strong>ar ais go dtí an Leathanach Baile</strong></strong</a></div>";
}



print <<"END_MESSAGE";
			</div>
		</div>
	</body>
</html>
END_MESSAGE


##################################################################
##################################################################
##################################################################.


