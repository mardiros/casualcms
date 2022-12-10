import { expect } from "chai";

import { toHtml } from "../../../../src/webapp/ui/components/richtext/serializer";
import { SlateModel } from "../../../../src/webapp/ui/components/richtext/types";

describe("Convert SlateModel to HTML", () => {
  it("Rebuild html paragraph extract the text", () => {
    const model: SlateModel = [
      {
        children: [
          {
            type: "TEXT",
            text: "My lazy dog",
          },
        ],
        type: "paragraph",
      },
    ];
    const html = toHtml(model);
    expect(html).eql("<p>My lazy dog</p>");
  });

  it("Rebuild html paragraph extract the bold text", () => {
    const model: SlateModel = [
      {
        children: [
          {
            type: "TEXT",
            text: "My ",
          },
          {
            type: "TEXT",
            text: "lazy",
            bold: true,
          },
          {
            type: "TEXT",
            text: " dog",
          },
        ],
        type: "paragraph",
      },
    ];
    const html = toHtml(model);
    expect(html).eql("<p>My <strong>lazy</strong> dog</p>");
  });

  it("Rebuild html title and paragraph", () => {
    const model: any = [
      {
        type: "h1",
        children: [
          {
            type: "TEXT",
            text: "Title",
          },
        ],
      },
      {
        type: "paragraph",
        children: [
          {
            type: "TEXT",
            text: "My lazy dog",
          },
        ],
      },
      {
        type: "h2",
        children: [
          {
            type: "TEXT",
            text: "Subtitle",
          },
        ],
      },
      {
        type: "paragraph",
        children: [
          {
            type: "TEXT",
            text: "ha ha!",
          },
        ],
      },
    ];
    const html = toHtml(model);
    expect(html).eql("<h1>Title</h1><p>My lazy dog</p><h2>Subtitle</h2><p>ha ha!</p>");
  });
  it("Parse unordered list", () => {
    const model: SlateModel = [
      {
        type: "ul",
        children: [
          {
            type: "li",
            children: [
              {
                type: "TEXT",
                text: "Dog",
              },
            ],
          },
          {
            type: "li",
            children: [
              {
                type: "TEXT",
                text: "Cat",
              },
            ],
          },
          {
            type: "li",
            children: [
              {
                type: "TEXT",
                text: "Lezard",
              },
            ],
          },
        ],
      },
    ];
    const html = toHtml(model);
    expect(html).eql("<ul><li>Dog</li><li>Cat</li><li>Lezard</li></ul>");
  });

  it("Parse ordered list", () => {
    const model: SlateModel = [
      {
        type: "ol",
        children: [
          {
            type: "li",
            children: [
              {
                type: "TEXT",
                text: "Dog",
              },
            ],
          },
          {
            type: "li",
            children: [
              {
                type: "TEXT",
                text: "Cat",
              },
            ],
          },
          {
            type: "li",
            children: [
              {
                type: "TEXT",
                text: "Lezard",
              },
            ],
          },
        ],
      },
    ];
    const html = toHtml(model);
    expect(html).eql("<ol><li>Dog</li><li>Cat</li><li>Lezard</li></ol>");
  });
  it("Serialize link", () => {
    const model: SlateModel = [
      {
        type: "paragraph",
        children: [
          {
            type: "link",
            href: "https://2.cv/",
            children: [
              {
                type: "TEXT",
                text: "la dodoche",
              },
            ],
          },
          {
            type: "TEXT",
            text: " is a french car.",
          },
        ],
      },
    ];
    const html = toHtml(model);
    expect(html).eql('<p><a href="https://2.cv/">la dodoche</a> is a french car.</p>');
  });
});
