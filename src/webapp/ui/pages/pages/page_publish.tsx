import React from "react";
import {
  Box,
  Button,
  Checkbox,
  CheckboxGroup,
  Icon,
  Popover,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverHeader,
  PopoverTrigger,
  Portal,
  Stack,
  useDisclosure,
} from "@chakra-ui/react";
import { DownloadIcon, SunIcon, ViewIcon } from "@chakra-ui/icons";
import { ApiError, ApiResult } from "../../../casualcms/domain/ports";
import { useConfig } from "../../../config";
import { PartialSite } from "../../../casualcms/domain/model";
import { Loader } from "../../components/loader";

type PublishButtonProps = {
  token: string;
  pagePath: string;
};

export type SelectableHostname = {
  hostname: string;
  secure: boolean;
  root_page_path: string;
  selected: boolean;
  response?: ApiResult<boolean>;
};

type SiteCheckBoxProps = {
  hostname: SelectableHostname;
};

type SiteListBoxProps = {
  hostnames: SelectableHostname[];
  onSubmit: React.MouseEventHandler<HTMLButtonElement>;
};

export const SiteListBox: React.FunctionComponent<SiteListBoxProps> = (
  props: SiteListBoxProps,
) => {
  const { hostnames, onSubmit } = props;
  return (
    <>
      <CheckboxGroup>
        <Stack marginBottom={5} spacing={[5, 15]} direction={["column"]}>
          {hostnames.map((hostname) => (
            <SiteCheckBox key={hostname.hostname} hostname={hostname} />
          ))}
        </Stack>
      </CheckboxGroup>
      <Button colorScheme="cyan" onClick={onSubmit} role="publish">
        Submit
      </Button>
    </>
  );
};

function get_url(site: SelectableHostname, pagePath: string) {
  const localPath = pagePath.replace(site.root_page_path, "");
  if (site.secure) {
    return `https://${site.hostname}${localPath}`;
  }
  return `http://${site.hostname}${localPath}`;
}

type PublishResultBoxProps = {
  pagePath: string;
  hostnames: SelectableHostname[];
  onClose: React.MouseEventHandler<HTMLButtonElement>;
};

export const PublishResultBox: React.FunctionComponent<PublishResultBoxProps> = (
  props: PublishResultBoxProps,
) => {
  const { hostnames, pagePath, onClose } = props;
  return (
    <Box>
      <Stack p={4} spacing={4} direction="column" bg={"cyan.200"}>
        {hostnames.map((hostname) => (
          <Box key={hostname.hostname} role="publication_result">
            {
              {
                true: (
                  <>
                    {hostname.hostname}
                    &nbsp;
                    {(hostname.response?.isOk() && (
                      <a
                        role="view_publication_result"
                        target="_blank"
                        href={get_url(hostname, pagePath)}
                        rel="noreferrer"
                      >
                        <Icon
                          as={ViewIcon}
                          display="inline-block"
                          verticalAlign="center"
                          marginStart={20}
                        />
                        View
                      </a>
                    )) ||
                      "ERROR"}
                  </>
                ),
                false: <>{hostname.hostname}&nbsp;Ignored</>,
              }[hostname.selected.toString()]
            }
          </Box>
        ))}
      </Stack>
      <Button colorScheme="cyan" onClick={onClose} role="close_publish_popover">
        Close
      </Button>
    </Box>
  );
};

export const SiteCheckBox: React.FunctionComponent<SiteCheckBoxProps> = (
  props: SiteCheckBoxProps,
) => {
  const { hostname } = props;
  return (
    <Checkbox
      role="select_site"
      value={hostname.hostname}
      colorScheme={"cyan"}
      onChange={(e) => {
        hostname.selected = e.target.checked;
      }}
      isChecked={hostname.selected}
    >
      {hostname.hostname}
    </Checkbox>
  );
};

export const PublishButton: React.FunctionComponent<PublishButtonProps> = (
  props: PublishButtonProps,
) => {
  const { token, pagePath } = props;
  const { onOpen, onClose, isOpen } = useDisclosure();
  const [publishedState, setPublishedState] = React.useState<
    "closed" | "loading" | "begin" | "done"
  >("closed");
  const [error, setError] = React.useState<ApiError>(null);
  const [hostnames, setHostnames] = React.useState<SelectableHostname[]>([]);
  const config = useConfig();
  const onSubmit = async () => {
    const pages = hostnames
      .filter((el) => el.selected)
      .map((el) => config.api.page.publishPage(token, el.hostname, pagePath));
    const resps = await Promise.all(pages);
    hostnames.filter((el) => el.selected).map((el) => (el.response = resps.shift()));
    setPublishedState("done");
  };
  React.useEffect(() => {
    async function loadSites() {
      let sites: ApiResult<PartialSite[]>;
      sites = await config.api.site.listSites(token);
      const hostnamesLoaded: SelectableHostname[] = [];
      sites
        .map((sites: PartialSite[]) => {
          sites
            .filter((el) => pagePath.startsWith(el.root_page_path))
            .map((el) =>
              hostnamesLoaded.push({
                hostname: el.hostname,
                selected: false,
                secure: el.secure,
                root_page_path: el.root_page_path,
              }),
            );
        })
        .mapErr((err: ApiError) => setError(err)); // FIXME
      setPublishedState("begin");
      setHostnames(hostnamesLoaded);
    }
    if (token && publishedState === "loading") {
      loadSites();
    }
    return function cleanup() {};
  }, [token, publishedState]);

  return (
    <Popover
      isOpen={isOpen}
      onOpen={() => {
        setPublishedState("loading");
        onOpen();
      }}
      onClose={() => {
        setPublishedState("closed");
        onClose();
      }}
      placement="right"
    >
      <PopoverTrigger>
        <Button colorScheme="cyan" role="open_publish_popover" leftIcon={<SunIcon />}>
          Publish
        </Button>
      </PopoverTrigger>
      <Portal>
        <PopoverContent backgroundColor={"cyan.200"}>
          <PopoverHeader>
            {
              {
                closed: "...",
                loading: "Choose website(s)",
                begin: "Choose website(s)",
                done: "Publication Report",
              }[publishedState]
            }
          </PopoverHeader>
          <PopoverCloseButton />
          <PopoverBody>
            {
              {
                closed: <></>,
                loading: <Loader label="Loading sites" />,
                begin: <SiteListBox hostnames={hostnames} onSubmit={onSubmit} />,
                done: (
                  <PublishResultBox
                    hostnames={hostnames}
                    pagePath={pagePath}
                    onClose={onClose}
                  />
                ),
              }[publishedState]
            }
          </PopoverBody>
        </PopoverContent>
      </Portal>
    </Popover>
  );
};
export const PageEditButtons: React.FunctionComponent<PublishButtonProps> = (
  props: PublishButtonProps,
) => {
  return (
    <Stack paddingTop={5} direction="row" align="right">
      <Button
        form="edit-page"
        type="submit"
        colorScheme="cyan"
        leftIcon={<DownloadIcon />}
      >
        Save
      </Button>
      <PublishButton token={props.token} pagePath={props.pagePath} />
    </Stack>
  );
};
