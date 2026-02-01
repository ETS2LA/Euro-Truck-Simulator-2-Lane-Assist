using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace Extractor
{
    public static class TextUtils
    {
        /// <summary>
        /// Finds quoted path-like strings in a .sii/.sui file.
        /// </summary>
        /// <param name="text">The text of the file.</param>
        /// <returns>Start and end positions of quoted strings in this file.</returns>
        public static List<Range> FindQuotedPaths(string text)
        {
            List<Range> ranges = [];
            int i;
            int startingQuotePos = -1;
            bool dotOrSlashFound = false;
            for (i = 0; i < text.Length; i++)
            {
                char c = text[i];

                if (startingQuotePos >= 0)
                {
                    bool isStringEnd = (c == '"' && !LookBack('\\')) || c == '\r' || c == '\n';
                    if (isStringEnd)
                    {
                        if (dotOrSlashFound)
                        {
                            ranges.Add(new Range(startingQuotePos + 1, i));
                            dotOrSlashFound = false;
                        }
                        startingQuotePos = -1;
                    }
                    else if (c == '.' || c == '/')
                    {
                        dotOrSlashFound = true;
                    }
                }
                else
                {
                    bool isStringStart = c == '"' && !LookBack('\\');
                    if (isStringStart)
                    {
                        startingQuotePos = i;
                    }
                    // Ignore single-line comment with #
                    else if (c == '#')
                    {
                        SkipUntil('\n');
                    }
                    else if (c == '/')
                    {
                        // Ignore single-line comment with //
                        if (Peek('/')) SkipUntil('\n');
                        // Ignore C-style multi-line comment
                        else if (Peek('*')) SkipUntilStr("*/");
                    }
                }
            }

            return ranges;

            bool Peek(char c)
            {
                return i < text.Length - 1 && text[i + 1] == c;
            }

            bool LookBack(char c)
            {
                return i > 0 && text[i - 1] == c;
            }

            void SkipUntil(char c)
            {
                for (; i < text.Length - 1 && text[i] != c; i++);
            }

            void SkipUntilStr(string s)
            {
                for (; i < text.Length - 1; i++)
                {
                    if (Equals(s))
                    {
                        i += s.Length - 1;
                        return;
                    }
                }
            }

            bool Equals(string s)
            {
                for (int j = 0; j < s.Length; j++)
                {
                    if (s[j] != text[i + j])
                        return false;
                }
                return true;
            }
        }

        /// <summary>
        /// Replaces character ranges in a string with a substitution if one is provided.
        /// </summary>
        /// <param name="text">The input text.</param>
        /// <param name="ranges">An ordered list of character ranges to replace if necessary.</param>
        /// <param name="substitutions">The substitutions to be made.</param>
        /// <returns>A version of the text in which all character ranges for which a substituion
        /// exists have been updated accordingly.</returns>
        public static (string Text, bool Modified) ReplaceStrings(string text, List<Range> ranges, 
            Dictionary<string, string> substitutions)
        {
            var sb = new StringBuilder();
            var textSpan = text.AsSpan();
            var modified = false;

            int prev = 0;
            foreach (Range range in ranges)
            {
                sb.Append(textSpan[prev..range.Start]);
                var target = textSpan[range];
                if (substitutions.TryGetValue(target.ToString(), out var substitution))
                {
                    sb.Append(substitution);
                    prev = range.End.Value;
                    modified = true;
                }
                else
                {
                    prev = range.Start.Value;
                }
            }
            sb.Append(textSpan[prev..]);

            return (sb.ToString(), modified);
        }

        public static (string Text, bool Modified) ReplaceRenamedPaths(string text,
            Dictionary<string, string> substitutions)
        {
            var modified = false;

            var ranges = FindQuotedPaths(text);
            if (ranges.Count > 0)
            {
                (text, modified) = ReplaceStrings(text, ranges, substitutions);
            }

            return (text, modified);
        }

        /// <summary>
        /// Converts a wildcard expression containing * and ? to a <see cref="Regex"/>.
        /// </summary>
        /// <param name="input">The wildcard expression.</param>
        /// <returns>The equivalent <see cref="Regex"/>.</returns>
        public static Regex WildcardStringToRegex(string input)
        {
            var sb = new StringBuilder();
            sb.Append('^');
            foreach (var c in input)
            {
                switch (c)
                {
                    case '?':
                        sb.Append('.');
                        break;
                    case '*':
                        sb.Append(".*");
                        break;
                    case '^':
                    case '$':
                    case '(':
                    case ')':
                    case '[':
                    case ']':
                    case '{':
                    case '}':
                    case '.':
                    case '+':
                    case '|':
                    case '\\':
                        sb.Append('\\');
                        sb.Append(c);
                        break;
                    default:
                        sb.Append(c);
                        break;
                }
            }
            sb.Append('$');
            return new Regex(sb.ToString());
        }

        public static bool MatchesFilters(IList<Regex> filters, string str)
        {
            if (filters is null)
                return true;

            foreach (var filter in filters)
            {
                if (filter.IsMatch(str))
                    return true;
            }
            return false;
        }
    }
}
