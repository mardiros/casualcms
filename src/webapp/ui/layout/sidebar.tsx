import { Box, SimpleGrid } from "@chakra-ui/react";
import { Link, useLocation } from "react-router-dom";

const menuStyle = {
  display: "block",
  padding: "0.5em",
};

type SideBarItemProps = {
  colors: string[];
  href: string;
  title: string;
};

export const SideBarItem: React.FunctionComponent<SideBarItemProps> = (
  props: SideBarItemProps
) => {
  const { colors, href, title } = props;
  return (
    <Box
      bg={colors[0]}
      borderRadius="md"
      color={colors[1]}
      margin={2}
      marginBottom={0}
    >
      <Link to={href} style={menuStyle} data-selected={colors[2]}>
        {title}
      </Link>
    </Box>
  );
};

export const SideBar: React.FunctionComponent<{}> = () => {
  const selectedColor = ["teal.50", "black", "true"];
  let pagesColor = ["teal.500", "white", "false"];
  let sitesColor = ["teal.500", "white", "false"];
  let snippetsColor = ["teal.500", "white", "false"];
  let settingsColor = ["teal.500", "white", "false"];
  const location = useLocation();
  if (
    location.pathname.startsWith("/admin/pages") ||
    location.pathname == "/admin/"
  ) {
    pagesColor = selectedColor;
  } else if (location.pathname.startsWith("/admin/sites")) {
    sitesColor = selectedColor;
  } else if (location.pathname.startsWith("/admin/snippets")) {
    snippetsColor = selectedColor;
  } else if (location.pathname.startsWith("/admin/settings")) {
    settingsColor = selectedColor;
  } else {
    return <></>;
  }

  return (
    <Box
      minWidth={250}
      height="calc(100vh - 90px)"
      bgColor="teal.300"
      color="white"
    >
      <SimpleGrid columns={1} spacing={1}>
        <SideBarItem colors={pagesColor} href="/admin/pages" title="Pages" />
        <SideBarItem
          colors={snippetsColor}
          href="/admin/snippets"
          title="Snippets"
        />
        <SideBarItem colors={sitesColor} href="/admin/sites" title="Sites" />
        <SideBarItem
          colors={settingsColor}
          href="/admin/settings"
          title="Settings"
        />
      </SimpleGrid>
    </Box>
  );
};
